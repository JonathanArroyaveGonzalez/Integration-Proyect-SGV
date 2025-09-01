""" Libraries """
import json
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from wmsAdapter.functions.TdaWmsConsultasAleatorias.TdaWmsArt import create_TdaWmsArt_from_dynamic_queries
from wmsAdapter.functions.TdaWmsConsultasAleatorias.TdaWmsClt import create_TdaWmsClt_from_dynamic_queries
from wmsAdapter.functions.TdaWmsConsultasAleatorias.TdaWmsDpk import create_TdaWmsDpk_from_dynamic_queries
from wmsAdapter.functions.TdaWmsConsultasAleatorias.TdaWmsEpk import create_TdaWmsEpk_from_dynamic_queries
from wmsAdapter.functions.TdaWmsConsultasAleatorias.TdaWmsPrv import create_TdaWmsPrv_from_dynamic_queries

""" Models and functions """
from wmsAdapter.utils.utils import exec_query
from wmsAdapter.models import TdaWmsArt, TdaWmsConsultasDinamicas
from wmsAdapter.functions.TdaWmsArt.create import create_articles

@csrf_exempt
def execute_consultas_dinamicas_from_origen(request):
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

            # Origen 
            origen = request.GET.get('origen', None)

            # Tabla destino
            tabla_destino = request.GET.get('tabla_destino', None)

            # Check if code is not null
            if codigo == None:
                return not_acceptable("The parameter codigo is required")

            # Check if origen is not null
            if origen == None:
                return not_acceptable("The parameter origen is required")
            
            # Check if tabla_destino is not null
            if tabla_destino == None:
                return not_acceptable("The parameter tabla_destino is required")

            # Initialize query
            consulta = None

            # Initialize parameters
            parametros_dict = None


            # Get the query from the database
            try:
                consulta = TdaWmsConsultasDinamicas.objects.using(origen).get(codigo=codigo)

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

            try:
                # Execute the query
                response = exec_query(query, (), database=origen)

                print(len(response))


                # articles
                if tabla_destino == 'TdaWmsArt':
                    try:
                        # Create articles
                        response = create_TdaWmsArt_from_dynamic_queries(response,db_name)
                        return JsonResponse(response, safe=False, status=200)
                            
                    except Exception as e:
                        return server_error(str(e))

                # customers
                elif tabla_destino == 'TdaWmsClt':
                    try:
                        # Create clt
                        response = create_TdaWmsClt_from_dynamic_queries(response,db_name)
                        return JsonResponse(response, safe=False, status=200)
                            
                    except Exception as e:
                        return server_error(str(e))
                    
                elif tabla_destino == 'TdaWmsPrv':
                    try:
                        # Create prv
                        response = create_TdaWmsPrv_from_dynamic_queries(response,db_name)
                        return JsonResponse(response, safe=False, status=200)
                            
                    except Exception as e:
                        return server_error(str(e))
                    
                elif tabla_destino == 'TdaWmsEpk':
                    try:
                        # Create epk
                        response = create_TdaWmsEpk_from_dynamic_queries(response,db_name)
                        return JsonResponse(response, safe=False, status=200)
                            
                    except Exception as e:
                        return server_error(str(e))
                
                elif tabla_destino == 'TdaWmsDpk':
                    try:
                        # Create dpk
                        response = create_TdaWmsDpk_from_dynamic_queries(response,db_name)
                        return JsonResponse(response, safe=False, status=200)
                            
                    except Exception as e:
                        return server_error(str(e))
                    
                else:
                    return JsonResponse({'error' : 'Invalid table'}, safe=False, status=403)

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