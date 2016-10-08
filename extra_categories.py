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
    'com.endlessm.animals': ['Reference', 'Family'],
    'com.endlessm.astronomy': ['Reference', 'Family'],
    'com.endlessm.biology': ['Reference'],
    'com.endlessm.childrens_collection': ['Education'],
    'com.endlessm.cooking': ['Family'],
    'com.endlessm.creativity_center': ['Education', 'Family'],
    'com.endlessm.dinosaurs': ['Reference'],
    'com.endlessm.disabilities': ['Family'],
    'com.endlessm.diy': ['Family'],
    'com.endlessm.encyclopedia': ['Education'],
    'com.endlessm.entrepreneurship': ['Education'],
    'com.endlessm.farming': ['Education'],
    'com.endlessm.finance': ['Family'],
    'com.endlessm.fitness': ['Family'],
    'com.endlessm.guatemala': ['Reference', 'Family'],
    'com.endlessm.guatemalan_curriculum': ['Reference'],
    'com.endlessm.health': ['Family'],
    'com.endlessm.healthy_living': ['Family'],
    'com.endlessm.healthy_teeth': ['Family'],
    'com.endlessm.howto': ['Family'],
    'com.endlessm.library': ['Education'],
    'com.endlessm.maternity': ['Family'],
    'com.endlessm.mayan_languages': ['Reference', 'Family'],
    'com.endlessm.mental_health': ['Family'],
    'com.endlessm.myths': ['Reference', 'Family'],
    'com.endlessm.programming': ['Game'],
    'com.endlessm.resume': ['Family'],
    'com.endlessm.soccer': ['Family'],
    'com.endlessm.spanish_guarani_dictionary': ['Education'],
    'com.endlessm.translation': ['Office', 'Family'],
    'com.endlessm.travel': ['Family'],
    'com.endlessm.videonet': ['Education', 'Family'],
    'com.endlessm.water_and_sanitation': ['Family'],
    'com.endlessm.weather': ['Utility', 'Family'],
    'com.endlessm.your_health': ['Family']
}
