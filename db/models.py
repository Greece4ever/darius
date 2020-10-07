import pprint

class Model:
    def __init__(self,primary_key : bool = False,null : bool = True,unique : bool = False):
        self.primary_key = primary_key
        self.null = null
        self.unique = unique 
        
    def __activate__(self, name):
        pass

class Table:
    def __init__(self):
        self.fields = {}

    @classmethod
    def __activate__(self):
        collumns = self.__dict__
        self.collumns : dict = {}
        self.primary_key = {}
        if collumns is None:
            raise ValueError("No data were provided.")
        STATMENTS = []
        for collumn in collumns:
            view = collumns.get(collumn)
            if(issubclass(type(view),Model)):
                if(view.primary_key):
                    self.primary_key[collumn] = view
                STATMENTS.append(view.__activate__(collumn))
                self.collumns[collumn] = view

        if(len(STATMENTS) == 0):
            raise ValueError("No Models were provided in {}.".format(User.__name__))
        p_key_len : int = len(self.primary_key)
        
        # Configure Primary Key that can be accessed by other tables
        if(p_key_len > 1):
            raise ValueError(f"Table {self.__name__} has more than 1 primary key, it has {p_key_len}!")
        if(p_key_len == 1):
            p_key = list(self.primary_key.keys())[0]
            self.primary_key = [p_key,self.primary_key.get(p_key)]
        else:
            self.primary_key = None
        # fields = ",".join(STATMENTS)
        # pprint.pprint(self.primary_key)
        # pprint.pprint(self.collumns)
        return(
            f"CREATE TABLE {self.__name__}({fields})"
        )

class CharField(Model):    
    def __activate__(self, name):
        sql_statement = f'''
        "{name}" TEXT {"UNIQUE" if self.unique else ""} {"" if self.null else "NOT"} NULL {"PRIMARY KEY" if self.primary_key else ''}'''
        return sql_statement
    
class IntergerField(Model):
    def __init__(self,primary_key : bool = False,null : bool = True,unique : bool = False):
        self.primary_key = primary_key
        self.null = null
        self.unique = unique 
    
    def __activate__(self,name):
        sql_statement = f'''
        "{name}" INTEGER {"UNIQUE" if self.unique else ""} {"" if self.null else "NOT"} NULL {"PRIMARY KEY" if self.primary_key else ''}'''
        return sql_statement

class DecimalField(Model):
    def __activate__(self,name):
        sql_statement = f'''
            "{name}" REAL {"UNIQUE" if self.unique else ""} {"" if self.null else "NOT"} NULL {"PRIMARY KEY" if self.primary_key else ''}'''
        return sql_statement

class ForeginKey(Model):
    def __init__(self, reference_model : Model ,*args, **kwargs):
        self.reference_model = reference_model
        try:
            if(type(self.reference_model.primary_key) != list):
                raise ValueError(f"Reference table {self.reference_model} cannot be used as a Foreign key")
        except:
            raise ValueError(f"Reference table {self.reference_model} cannot be used as a Foreign key")
        super(ForeginKey, self).__init__(*args, **kwargs)

    def __activate__(self, name):
        sql_statement = f'''
        "{name}" INTEGER {"UNIQUE" if self.unique else ""} {"" if self.null else "NOT"} NULL {"PRIMARY KEY" if self.primary_key else ''},
        "{name}" references {self.reference_model}(id)'''
        return sql_statement

class ManyToManyField(ForeginKey):
    def __activate__(self, name):
        sql_statement = f'''
        "{name}" references {self.reference_model}(id)'''
        return sql_statement

class OneToOneField:
    pass

class User(Table):
    id = IntergerField(primary_key=True,null=False)
    username = CharField(null=False,unique=True)
    password = CharField(null=False,unique=False)
    email = CharField(null=True,unique=True)

class Msg(Table):
    id = IntergerField(primary_key=True)
    

if __name__ == "__main__":
    print(
        User.__activate__()
        # f"CREATE TABLE {User.__name__}({fields})"
    )