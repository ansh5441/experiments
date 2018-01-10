# Created by ansh on 12/7/16, 3:27 PM
class Tagger:
    def __init__(self):
        self.tag_dictionary = {
            'default': 'default.png',
            'new_user': 'new_user.png',
            'pokestop': 'Pokeball-36.png',
        }

    def get_image_from_tag(self, tag):
        return 'https://hifitestbkt.s3.amazonaws.com/tag_images/' + self.tag_dictionary.get(
            tag, self.tag_dictionary.get('default'))
