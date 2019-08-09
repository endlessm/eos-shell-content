# These are extra categories for Endless apps that are added
# to the content.json that become embedded in the appstream XML.
# This is a hack to workaround the limitation that the CMS
# specifies only a single category per app.
# Do not list upstream Linux apps here, as they are handled
# in the external categorization specified in gnome-software-data,
# which works with core apps and will continue to work as we
# transition from our own packaging of those apps to using
# flatpaks from upstream repos.

EXTRA_CATEGORIES = {
    'com.endlessm.childrens_collection': ['Education'],
    'com.endlessm.creativity_center': ['Education'],
    'com.endlessm.dinosaurs': ['Reference'],
    'com.endlessm.encyclopedia': ['Education'],
    'com.endlessm.entrepreneurship': ['Education'],
    'com.endlessm.farming': ['Education'],
    'com.endlessm.guatemala': ['Reference'],
    'com.endlessm.guatemalan_curriculum': ['Reference'],
    'com.endlessm.library': ['Education'],
    'com.endlessm.mayan_languages': ['Reference'],
    'com.endlessm.programming': ['Game'],
    'com.endlessm.spanish_guarani_dictionary': ['Education'],
    'com.endlessm.translation': ['Office']
}
