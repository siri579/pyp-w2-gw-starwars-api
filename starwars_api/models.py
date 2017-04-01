from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()


class BaseModel(object):
    RESOURCE_NAME=None
    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        for key,value in json_data.items():
            setattr(self,key,value)
            

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        method = 'get_{}'.format(cls.RESOURCE_NAME)
        method_name = getattr(api_client, method)
        
        json_data = method_name(resource_id)
        return cls(json_data)
         

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        # if cls.RESOURCE_NAME == 'people':
        #     return PeopleQuerySet()
        # elif cls.RESOURCE_NAME =='films':
        #     return FilmsQuerySet()
        
        query_name = '{}QuerySet()'.format(cls.RESOURCE_NAME.title())
        return eval(query_name)
        


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):
    RESOURCE_NAME = None
    def __init__(self):
        self.current_page = 1
        self.current_element = 0
        self._count = None
        self.objects = []
        
       

    def __iter__(self):
        return self.__class__()

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        while True:
            if self.current_element + 1 > len(self.objects):
            # need to request a new page
                try:
                    self._get_next_page()
                except SWAPIClientError:
                    raise StopIteration()
            elem = self.objects[self.current_element]
            self.current_element += 1
            return elem
        
    
    
    def _get_next_page(self):
        
        obj = getattr(api_client,"get_{}".format(self.RESOURCE_NAME))(**{'page': self.current_page})
        self._count = obj['count']
        self.current_page +=1
        Model = eval(self.RESOURCE_NAME.title())
        for item in obj['results']:
            self.objects.append(Model(item))
        
    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        if self._count is None:
            self._get_next_page()
        return self._count


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
