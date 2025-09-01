""" Libraries """
import json
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

""" Models and functions """
from wmsAdapter.utils.utils import exec_query
from wmsAdapter.models import TdaWmsConsultasDinamicas

""" View """
@csrf_exempt
def execute_consultas_dinamicas(request):

    """ 
        This function execute a query from the table TdaWmsConsultasDinamicas
        and return the result of the query  

        Method: POST
        Parameters: 
            codigo: code of the query
            parametros: parameters of the query

    """

    try:
        # Get the database name 
        db_name = request.db_name

    except Exception as e:
        return JsonResponse({
                                "error": "Unauthorized",
                                "message": "Authentication failed. Please check your credentials."
                                }, safe=False, status=401)

    # POST method
    if request.method == 'POST':

        try:
            # Get code and parameters
            codigo = request.GET.get('codigo', None)

            # Check if code is not null
            if codigo == None:
                return not_acceptable("The parameter codigo is required")

            # Initialize query
            consulta = None

            # Initialize parameters
            parametros_dict = None


            # Get the query from the database
            try:
                consulta = TdaWmsConsultasDinamicas.objects.using(db_name).get(codigo=codigo)

            except Exception as e:
                return not_acceptable("The code is not valid")
            
            # Check if the query is not null
            if consulta == None:
                return not_acceptable("The code is not valid")
            
            # Get the query
            query = consulta.query

            # Check if the query is not null
            if query == None:
                return not_acceptable("The query is not valid")

            # Check if the query has parameters
            if '{' in query and '}' in query:
                
                # Get the parameters
                if(request.body):
                    parametros_dict = json.loads(request.body)

                # Check if the parameters are not null
                if parametros_dict == None:
                    return not_acceptable("The query has parameters, please send the parameters")
                
                # Replace the parameters in the query
                for key, value in parametros_dict.items():

                    # Check if the value is in the query
                    if '{' + str(key) + '}' not in query:
                        return not_acceptable("The parameter " + str(key) + " is not valid")

                    # Replace the parameter
                    query = query.replace('{' + str(key) + '}', str(value))

            # Add SET NOCOUNT ON to the query
            query = """ 
                SET NOCOUNT ON; 
                """ + str(query)

            print(query)

            try:
                # Execute the query using the connection string on the table TdaWmsConsultasDinamicas 
                connection_string = consulta.conexion
                if connection_string == None or connection_string == "":
                    response = exec_query(query, (), database=db_name)
                else:
                    response = exec_query(query, (), database=connection_string)
                return JsonResponse(response, safe=False, status=200)
            
            except Exception as e:
                return  server_error(str(e))
            
        except Exception as e:
            return  server_error(str(e))


# Not acceptable
def not_acceptable(message):
    return JsonResponse({
                    "error": "user error",
                    "message": message
                    }, safe=False, status=406)

# Server error
def server_error(message):

    if "Incorrect syntax near '='." in message:
        return JsonResponse({
                    "error": "user error",
                    "message": "The parameter is not valid",
                    "tip" : "Maybe the parameter is not a number and the query must be adjusted like this: '{parameter}'"
                    }, safe=False, status=406)

    return JsonResponse({
                    "error": "server error",
                    "message": message
                    }, safe=False, status=500)