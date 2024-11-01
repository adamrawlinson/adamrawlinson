"""
Idea for a way to dynamically build SQL SELECT and WHERE statements
"""

# TODO (1): Way to append further *args / **kwargs to growing SQL select / where statements.
# TODO (2): Include FROM, JOINS, GROUP BY, HAVING and ORDER BY statemtents.
# TODO (3): Include CTE 

class SQLBuilder():

    def __init__(self):
        pass

    def col_selection(self, *selection_args):
        self.selection_args = selection_args
        
        self.selection_text = 'SELECT '
        for arg in self.selection_args[:-1]:
            self.selection_text += f'{arg}, '

        self.selection_text += self.selection_args[-1]
    
    def where_clause(self, first_arg: str = '', **where_kwargs):
        """
        **where_kwargs:
            key should be 'w_and' or 'w_or', value should be string clause.        
        """
        self.where_kwargs = where_kwargs

        self.where_text = f'WHERE {first_arg} '
        for key, value in self.where_kwargs.items():
            if key.lower() == 'w_and':
                self.where_text += f'AND {value} '
            elif key.lower() == 'w_or':
                self.where_text += f'OR {value} '
    

sqlbuild = SQLBuilder()
sqlbuild.col_selection('DATETIME', 'ARG_WORKS', 'LOCATION', 'CHECK2', 'ARG_WORKS')
sqlbuild.where_clause("MATER = 'Howdy Pardner'", w_and="fog = 'low'", w_or='LOCATION = 1')


# print(sqlbuild.selection_text)
# print(sqlbuild.where_text)
# Returns:
# SELECT DATETIME, ARG_WORKS, LOCATION, CHECK2, ARG_WORKS
# WHERE MATER = 'Howdy Pardner' AND fog = 'low' OR LOCATION = 1

