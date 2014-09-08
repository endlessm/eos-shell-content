#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <locale.h>

#include <glib-object.h>
#include <json-glib/json-glib.h>

static const char *translatable_keys[] = {
  "title",
  "subtitle",
  "description",
  "folderName"
};

static const int n_translatable_keys = G_N_ELEMENTS (translatable_keys);

static void
parse_content_array (JsonArray  *array,
                     const char *path,
                     GString    *buffer)
{
  guint n_elements = json_array_get_length (array);
  if (n_elements == 0)
    return;

  g_string_append_printf (buffer, "\n/* Extracted from %s */\n", path);

  for (guint i = 0; i < n_elements; i++)
    {
      JsonNode *element = json_array_get_element (array, i);

      if (!JSON_NODE_HOLDS_OBJECT (element))
        continue;

      JsonObject *obj = json_node_get_object (element);

      for (guint j = 0; j < n_translatable_keys; j++)
        {
          if (!json_object_has_member (obj, translatable_keys[j]))
            continue;

          const char *key = translatable_keys[j];
          const char *value = json_object_get_string_member (obj, key);

          g_string_append_printf (buffer, "\nC_(\"%s\", \"%s\");", key, value);
        }
    }
}

int
main (int   argc,
      char *argv[])
{
  setlocale (LC_ALL, "");

  if (argc < 3)
    {
      g_printerr ("Usage: extract-content-strings <content file> <output file>\n");
      return EXIT_FAILURE;
    }

  JsonParser *parser = json_parser_new ();
  const char *content_path = argv[1];
  const char *output_path = argv[2];

  GError *error = NULL;
  json_parser_load_from_file (parser, content_path, &error);
  if (error != NULL)
    {
      fprintf (stderr, "Unable to load content: %s\n", error->message);
      g_error_free (error);
      g_object_unref (parser);
      return EXIT_FAILURE;
    }

  JsonNode *root = json_parser_get_root (parser);
  if (root == NULL)
    {
      g_printerr ("Empty content\n");
      g_object_unref (parser);
      return EXIT_FAILURE;
    }

  if (!JSON_NODE_HOLDS_ARRAY (root))
    {
      g_printerr ("Malformed content: array required.\n");
      g_object_unref (parser);
      return EXIT_FAILURE;
    }

  GString *buffer = g_string_new ("");

  parse_content_array (json_node_get_array (root), content_path, buffer);

  g_object_unref (parser);

  GFile *file = g_file_new_for_path (output_path);
  g_file_replace_contents (file,
                           buffer->str,
                           buffer->len,
                           NULL,
                           FALSE,
                           G_FILE_CREATE_NONE,
                           NULL,
                           NULL,
                           &error);
  if (error != NULL)
    {
      fprintf (stderr, "Unable to write extracted file: %s\n", error->message);
      g_error_free (error);
      g_string_free (buffer, TRUE);
      return EXIT_FAILURE;
    }

  g_string_free (buffer, TRUE);

  return EXIT_SUCCESS;
}
