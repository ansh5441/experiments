human_data = {}
droid_data = {}
from graphene.test import Client

def setup():
    # from .schema import Human, Droid
    global human_data, droid_data
    luke = Human(
        id='1000',
        name='Luke Skywalker',
        friends=['1002', '1003', '2000', '2001'],
        appears_in=[4, 5, 6],
        home_planet='Tatooine',
    )

    vader = Human(
        id='1001',
        name='Darth Vader',
        friends=['1004'],
        appears_in=[4, 5, 6],
        home_planet='Tatooine',
    )

    han = Human(
        id='1002',
        name='Han Solo',
        friends=['1000', '1003', '2001'],
        appears_in=[4, 5, 6],
        home_planet=None,
    )

    leia = Human(
        id='1003',
        name='Leia Organa',
        friends=['1000', '1002', '2000', '2001'],
        appears_in=[4, 5, 6],
        home_planet='Alderaan',
    )

    tarkin = Human(
        id='1004',
        name='Wilhuff Tarkin',
        friends=['1001'],
        appears_in=[4],
        home_planet=None,
    )

    human_data = {
        '1000': luke,
        '1001': vader,
        '1002': han,
        '1003': leia,
        '1004': tarkin,
    }

    c3po = Droid(
        id='2000',
        name='C-3PO',
        friends=['1000', '1002', '1003', '2001'],
        appears_in=[4, 5, 6],
        primary_function='Protocol',
    )

    r2d2 = Droid(
        id='2001',
        name='R2-D2',
        friends=['1000', '1002', '1003'],
        appears_in=[4, 5, 6],
        primary_function='Astromech',
    )

    droid_data = {
        '2000': c3po,
        '2001': r2d2,
    }


def get_character(id):
    return human_data.get(id) or droid_data.get(id)


def get_friends(character):
    return map(get_character, character.friends)


def get_hero(episode):
    if episode == 5:
        return human_data['1000']
    return droid_data['2001']


def get_human(id):
    return human_data.get(id)


def get_droid(id):
    return droid_data.get(id)




import graphene

# from .data import get_character, get_droid, get_hero, get_human


class Episode(graphene.Enum):
    NEWHOPE = 4
    EMPIRE = 5
    JEDI = 6


class Character(graphene.Interface):
    id = graphene.ID()
    name = graphene.String()
    friends = graphene.List(lambda: Character)
    appears_in = graphene.List(Episode)

    def resolve_friends(self, info):
        # The character friends is a list of strings
        return [get_character(f) for f in self.friends]


class Human(graphene.ObjectType):

    class Meta:
        interfaces = (Character, )
    home_planet = graphene.String()


class Droid(graphene.ObjectType):

    class Meta:
        interfaces = (Character, )
    primary_function = graphene.String()


class Query(graphene.ObjectType):
    hero = graphene.Field(Character,
                          episode=Episode()
                          )
    human = graphene.Field(Human,
                           id=graphene.String()
                           )
    droid = graphene.Field(Droid,
                           id=graphene.String()
                           )

    def resolve_hero(self, info, episode=None):
        return get_hero(episode)

    def resolve_human(self, info, id):
        return get_human(id)

    def resolve_droid(self, info, id):
        return get_droid(id)


schema = graphene.Schema(query=Query)

setup()

client = Client(schema)


def test_hero_name_query():
    query = '''
        query HeroNameQuery {
          hero {
            name
          }
        }
    '''
    print("""""")
    print(client.execute(query))
    print("\n\n" + "_" * 120 + '\n')

test_hero_name_query()

def test_hero_name_and_friends_query():
    query = '''
        query HeroNameAndFriendsQuery {
          hero {
            id
            name
            friends {
              name
            }
          }
        }
    '''
    print("""""")
    print(client.execute(query))
    print("\n\n" + "_" * 120 + '\n')

test_hero_name_and_friends_query()

def test_nested_query():
    query = '''
        query NestedQuery {
          hero {
            name
            friends {
              name
              appearsIn
              friends {
                name
              }
            }
          }
        }
    '''
    print("""""")
    print(client.execute(query))
    print("\n\n" + "_" * 120 + '\n')

test_nested_query()

def test_fetch_luke_query():
    query = '''
        query FetchLukeQuery {
          human(id: "1000") {
            name
          }
        }
    '''
    print("""""")
    print(client.execute(query))
    print("\n\n" + "_" * 120 + '\n')

test_fetch_luke_query()

def test_fetch_some_id_query():
    query = '''
        query FetchSomeIDQuery($someId: String!) {
          human(id: $someId) {
            name
          }
        }
    '''
    params = {
        'someId': '1000',
    }
    print(client.execute(query, variable_values=params))

test_fetch_some_id_query()

def test_fetch_some_id_query2():
    query = '''
        query FetchSomeIDQuery($someId: String!) {
          human(id: $someId) {
            name
          }
        }
    '''
    params = {
        'someId': '1002',
    }
    print(client.execute(query, variable_values=params))

test_fetch_some_id_query2()

def test_invalid_id_query():
    query = '''
        query humanQuery($id: String!) {
          human(id: $id) {
            name
          }
        }
    '''
    params = {
        'id': 'not a valid id',
    }
    print(client.execute(query, variable_values=params))

test_invalid_id_query()

def test_fetch_luke_aliased():
    query = '''
        query FetchLukeAliased {
          luke: human(id: "1000") {
            name
          }
        }
    '''
    print("""""")
    print(client.execute(query))
    print("\n\n" + "_" * 120 + '\n')

test_fetch_luke_aliased()

def test_fetch_luke_and_leia_aliased():
    query = '''
        query FetchLukeAndLeiaAliased {
          luke: human(id: "1000") {
            name
          }
          leia: human(id: "1003") {
            name
          }
        }
    '''
    print("""""")
    print(client.execute(query))
    print("\n\n" + "_" * 120 + '\n')

test_fetch_luke_and_leia_aliased()

def test_duplicate_fields():
    query = '''
        query DuplicateFields {
          luke: human(id: "1000") {
            name
            homePlanet
          }
          leia: human(id: "1003") {
            name
            homePlanet
          }
        }
    '''
    print("""""")
    print(client.execute(query))
    print("\n\n" + "_" * 120 + '\n')

test_duplicate_fields()

def test_use_fragment():
    query = '''
        query UseFragment {
          luke: human(id: "1000") {
            ...HumanFragment
          }
          leia: human(id: "1003") {
            ...HumanFragment
          }
        }
        fragment HumanFragment on Human {
          name
          homePlanet
        }
    '''
    print("""""")
    print(client.execute(query))
    print("\n\n" + "_" * 120 + '\n')

test_use_fragment()

def test_check_type_of_r2():
    query = '''
        query CheckTypeOfR2 {
          hero {
            __typename
            name
          }
        }
    '''
    print("""""")
    print(client.execute(query))
    print("\n\n" + "_" * 120 + '\n')

test_check_type_of_r2()

def test_check_type_of_luke():
    query = '''
        query CheckTypeOfLuke {
          hero(episode: EMPIRE) {
            __typename
            name
          }
        }
    '''
    print("""""")
    print(client.execute(query))
    print("\n\n" + "_" * 120 + '\n')

test_check_type_of_luke()





