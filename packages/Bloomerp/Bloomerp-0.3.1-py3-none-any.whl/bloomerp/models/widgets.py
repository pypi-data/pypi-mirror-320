from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from bloomerp.models.core import BloomerpModel
from django.contrib.contenttypes.models import ContentType
from bloomerp.models.fields import CodeField

# ---------------------------------
# SQL Query Filter Model
# ---------------------------------
from bloomerp.utils.sql import SqlQueryExecutor
class SqlQueryFilter(BloomerpModel):
    '''
    A model to store filters for KPIs. Ech filter has a name and a query.
    '''
    class Meta(BloomerpModel.Meta):
        managed = True
        db_table = 'bloomerp_sql_query_filter'
        verbose_name = 'SQL Query Filter'
        verbose_name_plural = 'SQL Query Filters'

    class SqlQueryFilterOperations(models.TextChoices):
        EQUAL = '='
        GREATER = '>'
        LESS = '<'
        GREATER_OR_EQUAL = '>='
        LESS_OR_EQUAL = '<='
        NOT_EQUAL = '!='
        LIKE = 'LIKE'
        NOT_LIKE = 'NOT LIKE'
        IN = 'IN'
        NOT_IN = 'NOT IN'
        IS = 'IS'
        IS_NOT = 'IS NOT'
        BETWEEN = 'BETWEEN'
        NOT_BETWEEN = 'NOT BETWEEN'
        REGEXP = 'REGEXP'
        NOT_REGEXP = 'NOT REGEXP'
        EXISTS = 'EXISTS'
        NOT_EXISTS = 'NOT EXISTS'

    class SqlQueryFilterDataTypes(models.TextChoices):
        STRING = 'STRING'
        INTEGER = 'INTEGER'
        FLOAT = 'FLOAT'
        DATE = 'DATE'
        DATETIME = 'DATETIME'
        BOOLEAN = 'BOOLEAN'
        MODEL = 'MODEL'
        USER = 'USER'

    name = models.CharField(
        max_length=255,
        help_text='Name of the filter'
        )
    
    column = models.CharField(
        max_length=255, 
        help_text='Column name to filter on')
    
    filter_operation = models.CharField(
        max_length=255, 
        choices=SqlQueryFilterOperations,
        default=SqlQueryFilterOperations.EQUAL,
        help_text='Type of the filter'
        )
    
    data_type = models.CharField(
        max_length=255,
        choices=SqlQueryFilterDataTypes,
        default=SqlQueryFilterDataTypes.STRING,
        help_text='Data type of the filter'
        )

    filter_options = models.JSONField(blank=True, null=True)

    # Query executor
    executor = SqlQueryExecutor()

    def __str__(self):
        return self.name
    
    

# ---------------------------------
# SQL Query Model
# ---------------------------------
from django.contrib.auth.hashers import make_password
import time
class SqlQuery(BloomerpModel):
    '''
    A model to store SQL queries that can be used in Widgets
    '''
    class Meta(BloomerpModel.Meta):
        managed = True
        db_table = 'sql_query'
        verbose_name = 'SQL Query'
        verbose_name_plural = 'SQL Queries'
        permissions = [
            ('execute_sql_query', 'Can execute SQL queries')
            # Maybe add more permissions here corresponding to the actions that can be performed on the query
        ]

    name = models.CharField(max_length=255)
    query = CodeField(language='sql', help_text='SQL Query to execute')
    filters = models.ManyToManyField(SqlQueryFilter, blank=True)

    # String fields
    search_fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        start = time.time()

        # Initialize the query executor
        if self.pk is not None:
            self.executor = SqlQueryExecutor(
                cache_time=60,
                cache_id= str(self.pk) + self.name 
            )
        else:
            self.executor = SqlQueryExecutor()
    
    def is_safe(self):
        '''
        Check if the query is a SELECT statement
        '''
        return self.executor.is_safe(self.query)

    def result_dataframe(self):
        '''
        Execute the query and return the result
        '''
        return self.executor.execute_to_df(self.query)
        
    def result_dict(self):
        '''
        Execute the query and return the result
        '''
        return self.executor.execute_to_dict(self.query)
    
    def result_raw(self):
        '''
        Execute the query and return the result
        '''
        return self.executor.execute_raw(self.query)
    
    def result_value(self):
        '''
        Execute the query and return the result
        '''
        return self.executor.execute_to_first_value(self.query)

    def clean(self) -> None:
        '''
        Clean method does the following:
        - Check if the query is safe
        - Check if the query actually returns a result
        '''
        errors = {}

        # Check if the query is safe
        if not self.is_safe():
            errors['query'] = 'Unsafe query'

        # Check if the query returns a result
        result = self.executor.is_valid(self.query)
        if result != True:
            errors['query'] = result

        if errors:
            raise ValidationError(errors)


    def __str__(self):
        return self.name

    
# ---------------------------------
# Widget Model
# ---------------------------------
from pandas import DataFrame
class Widget(BloomerpModel):
    OUTPUT_TYPE_CHOICES = [
        ('table','Table'),
        ('value','Value'),
        ('line','Line chart'),
        ('bar','Bar chart'),
        ('pie','Pie chart'),
        ('scatter','Scatter chart'),
        ('histogram','Histogram')
    ]

    VALUE_AGGREGATE_CHOICES = [
        ('sum', 'Sum'),
        ('average', 'Average'),
        ('count', 'Count'),
        ('min', 'Minimum'),
        ('max', 'Maximum'),
        ('first', 'First value')
    ]

    name = models.CharField(max_length=255) # Name of the KPI
    query = models.ForeignKey(SqlQuery, on_delete=models.CASCADE) # Query to execute
    description = models.TextField(blank=True,null=True) # Description of the KPI
    output_type = models.CharField(choices=OUTPUT_TYPE_CHOICES, max_length=10)
    options = models.JSONField(blank=True,null=True)


    string_search_fields = ['name', 'description']
    allow_string_search = True


    def __str__(self):
        return self.name
    
    class Meta(BloomerpModel.Meta):
        managed = True
        db_table = 'bloomerp_widget'
    
    def clean(self):
        # SAFETY CHECKS
        if not self.query.is_safe:
            raise ValidationError('Unsafe query')

        # Get columns
        dataframe = self.query.result_dataframe()
        columns = dataframe.columns.tolist()

        # TABLE SPECIFIC VALIDATION
        if self.output_type == 'table':
            if self.options is None:
                raise ValidationError('Options are required for table KPIs')

            if 'columns' not in self.options:
                raise ValidationError('Columns are required for table KPIs')
            
            for col in self.options['columns']:
                if col not in columns:
                    raise ValidationError(f'Column {col} does not exist in the query result')
            if 'limit' not in self.options:
                self.options['limit'] = 10

            

        # GRAPH SPECIFIC VALIDATION
        if (self.output_type == 'bar' or self.output_type == 'line' or self.output_type == 'scatter') and self.options is None:
            raise ValidationError('Options are required for chart KPIs')

        
        # BAR / LINE / SCATTER SPECIFIC VALIDATION
        if self.output_type == 'bar' or self.output_type == 'line' or self.output_type == 'scatter':
            if 'x' not in self.options:
                raise ValidationError('X-axis is required for bar chart KPIs')
            else:
                if self.options['x'] not in columns:
                    raise ValidationError(f'Column {self.options["x"]} does not exist in the query result')
            
            if 'y' not in self.options:
                raise ValidationError('Y-axis is required for bar chart KPIs')
            else:
                if self.options['y'] not in columns:
                    raise ValidationError(f'Column {self.options["y"]} does not exist in the query result')

            if 'group_by' in self.options:
                if self.options['group_by'] not in columns:
                    raise ValidationError(f'Column {self.options["group_by"]} does not exist in the query result')

        # PIE SPECIFIC VALIDATION     
        if self.output_type == 'pie':
            if 'x' not in self.options:
                raise ValidationError('X-axis is required for pie chart KPIs')
            else:
                if self.options['x'] not in columns:
                    raise ValidationError(f'Column {self.options["x"]} does not exist in the query result')
            
            if 'group_by' not in self.options:
                raise ValidationError('Groupby column is required for pie chart KPIs')
            else:
                if self.options['group_by'] not in columns:
                    raise ValidationError(f'Column {self.options["y"]} does not exist in the query result')
                
        # HISTOGRAM SPECIFIC VALIDATION
        if self.output_type == 'histogram':
            if 'x' not in self.options:
                raise ValidationError('X-axis is required for histogram KPIs')
            else:
                if self.options['x'] not in columns:
                    raise ValidationError(f'Column {self.options["x"]} does not exist in the query result')
                
        # VALUE SPECIFIC VALIDATION
        if self.output_type == 'value':
            if 'color' not in self.options:
                self.options['color'] = 'gray'
            
            if 'prefix' not in self.options:
                self.options['prefix'] = ''

            if 'suffix' not in self.options:
                self.options['suffix'] = ''
            
            if 'icon' not in self.options:
                self.options['icon'] = 'bi bi-bar-chart'

            if 'column' not in self.options:
                raise ValidationError('Column is required for value KPIs')

            if 'aggregate' not in self.options:
                self.options['aggregate'] = 'first'
            
            if self.options['aggregate'] not in [agg[0] for agg in self.VALUE_AGGREGATE_CHOICES]:
                raise ValidationError('Invalid aggregate type')
            
    @property
    def result_value(self):
        '''
        Execute the query and return the result
        '''
        dataframe:DataFrame = self.query.result_dataframe()

        if self.output_type == 'value':
            column = self.options['column']
            aggregate = self.options['aggregate']

            try:
                if aggregate == 'sum':
                    return dataframe[column].sum()
                elif aggregate == 'average':
                    return dataframe[column].mean()
                elif aggregate == 'count':
                    return dataframe[column].count()
                elif aggregate == 'min':
                    return dataframe[column].min()
                elif aggregate == 'max':
                    return dataframe[column].max()
                elif aggregate == 'first':
                    return dataframe[column].iloc[0]
            except:
                self.options['aggregate'] = 'first'
                self.save()
                return dataframe[column].iloc[0]
        else:
            return 'Value result not available for this KPI type'

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

