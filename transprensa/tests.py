"""
Tests para el módulo Transprensa - Workflow y Mapper
"""

import base64
from unittest import TestCase
from unittest.mock import Mock, patch

from transprensa.functions.remesaMapper import (
    mapear_guia_a_remesa,
    remesa_a_dict,
    crear_payload_api,
    get_data_from_guia,
    create_guia_number,
    limpiar_espacios,
    obtener_codigo_dane,
    Remesa,
    Cliente,
    Remitente,
    Destinatario,
    Detalle,
    OSAKA_CLIENTE_CODIGO,
    OSAKA_REMITENTE_CODIGO,
)
from transprensa.functions.create import (
    execute_guide_workflow,
    download_pdf_from_url,
    _process_pdf_background,
)
from transprensa.services.transprensaService import TransprensaService


# ============================================================================
# DATOS DE PRUEBA
# ============================================================================

MOCK_GUIA_DATA = {
    "picking": "7746",
    "bigpedido": "PD-103888",
    "is_detail_0": {
        "data": [
            {
                "nit_destinatario": "900123456-7",
                "nombre_destinatario": "EMPRESA PRUEBA S.A.S",
                "direccion_destinatario": "Carrera 45 # 12-34",
                "telefono_destinatario": "3201234567",
                "ciudad_destinatario": "BOGOTA",
                "valor_declarado": "500000",
                "referencia": "REF-001",
                "observaciones": "Mercancía frágil",
            }
        ]
    },
    "is_detail_1": {
        "data": [
            {
                "peso_real": "2.5",
                "volumen": "0.025",
                "unidades": "3",
                "descripcion": "Productos electrónicos",
            }
        ]
    },
}

MOCK_TRANSPRENSA_CREATE_RESPONSE = {
    "success": True,
    "data": [{"remesa": "REM-12345", "validacion": ""}],
    "msg": "Remesa creada exitosamente",
}

MOCK_TRANSPRENSA_PRINT_RESPONSE = {
    "success": True,
    "data": {"REM-12345": "https://ejemplo.com/pdf/REM-12345.pdf"},
    "msg": "PDF generado exitosamente",
}


# ============================================================================
# TESTS DEL MAPPER
# ============================================================================


class TestRemesaMapper(TestCase):
    """Tests para las funciones del mapper de remesas."""

    def test_limpiar_espacios_con_string(self):
        """Test de limpieza de espacios en strings."""
        self.assertEqual(limpiar_espacios("  texto  "), "texto")
        self.assertEqual(limpiar_espacios("sin espacios"), "sin espacios")
        self.assertEqual(limpiar_espacios(""), "")

    def test_limpiar_espacios_con_no_string(self):
        """Test de limpieza cuando el valor no es string."""
        self.assertEqual(limpiar_espacios(None), None)
        self.assertEqual(limpiar_espacios(123), 123)
        self.assertEqual(limpiar_espacios([1, 2, 3]), [1, 2, 3])

    def test_create_guia_number(self):
        """Test de creación de número de guía."""
        result = create_guia_number("ABC7746XYZ", "PD-103888-DEF")
        self.assertEqual(result, "7746103888")

        result = create_guia_number("", "123")
        self.assertEqual(result, "123")

        result = create_guia_number("ABC", "")
        self.assertEqual(result, "")

        result = create_guia_number(None, None)
        self.assertEqual(result, "")

    @patch("transprensa.functions.remesaMapper.get_ciudad_codigo_by_nombre")
    def test_obtener_codigo_dane(self, mock_get_ciudad):
        """Test de obtención de código DANE."""
        mock_get_ciudad.return_value = "11001000"

        result = obtener_codigo_dane("BOGOTA")
        self.assertEqual(result, "11001000")
        mock_get_ciudad.assert_called_once_with("BOGOTA")

        # Test con ciudad vacía
        result = obtener_codigo_dane("")
        self.assertEqual(result, "05001000")  # Medellín por defecto

        # Test cuando no se encuentra ciudad
        mock_get_ciudad.return_value = None
        result = obtener_codigo_dane("CIUDAD_INEXISTENTE")
        self.assertEqual(result, "05001000")

    def test_get_data_from_guia_estructura_valida(self):
        """Test de extracción de datos de guía con estructura válida."""
        sin_detalle, con_detalle = get_data_from_guia(MOCK_GUIA_DATA)

        self.assertIsNotNone(sin_detalle)
        self.assertIsNotNone(con_detalle)
        self.assertEqual(sin_detalle["nit_destinatario"], "900123456-7")
        self.assertEqual(con_detalle["peso_real"], "2.5")

    def test_get_data_from_guia_estructura_invalida(self):
        """Test de extracción con estructura inválida."""
        invalid_data = {"invalid_key": "value"}
        result = get_data_from_guia(invalid_data)
        self.assertIsNone(result)

    @patch("transprensa.functions.remesaMapper.get_ciudad_codigo_by_nombre")
    def test_mapear_guia_a_remesa_exitoso(self, mock_get_ciudad):
        """Test de mapeo exitoso de guía a remesa."""
        mock_get_ciudad.return_value = "11001000"  # Código DANE de Bogotá

        remesa = mapear_guia_a_remesa(MOCK_GUIA_DATA)

        self.assertIsNotNone(remesa)
        self.assertIsInstance(remesa, Remesa)

        # Verificar datos del destinatario
        self.assertEqual(remesa.destinatario.destinatario_documento, "9001234567")
        self.assertEqual(
            remesa.destinatario.destinatario_nombre, "EMPRESA PRUEBA S.A.S"
        )
        self.assertEqual(remesa.destinatario.destinatario_ciudad_codigo, "11001000")

        # Verificar detalle
        self.assertEqual(remesa.detalle.detalle_peso, "2.5")
        self.assertEqual(remesa.detalle.detalle_volumen, "0.025")
        self.assertEqual(remesa.detalle.detalle_cantidad, "3")

        # Verificar constantes
        self.assertEqual(remesa.cliente.cliente_codigo, OSAKA_CLIENTE_CODIGO)
        self.assertEqual(remesa.remitente.remitente_codigo, OSAKA_REMITENTE_CODIGO)

    def test_mapear_guia_a_remesa_error(self):
        """Test de mapeo con datos inválidos."""
        invalid_data = {"invalid": "data"}
        result = mapear_guia_a_remesa(invalid_data)
        self.assertIsNone(result)

    def test_remesa_a_dict(self):
        """Test de conversión de Remesa a diccionario."""
        # Crear una remesa de prueba
        cliente = Cliente()
        remitente = Remitente()
        destinatario = Destinatario(
            destinatario_documento="123456789", destinatario_nombre="Test Cliente"
        )
        detalle = Detalle(detalle_peso="1.0", detalle_cantidad="1")

        remesa = Remesa(
            cliente=cliente,
            remitente=remitente,
            destinatario=destinatario,
            detalle=detalle,
            remesa_codigo="TEST-001",
        )

        result = remesa_a_dict(remesa)

        self.assertIsInstance(result, dict)
        self.assertIn("cliente", result)
        self.assertIn("remitente", result)
        self.assertIn("destinatario", result)
        self.assertIn("detalle", result)
        self.assertEqual(result["remesa_codigo"], "TEST-001")
        self.assertIsInstance(result["detalle"], list)

    def test_crear_payload_api(self):
        """Test de creación de payload para API."""
        # Crear remesas de prueba
        remesa1 = Remesa(
            cliente=Cliente(),
            remitente=Remitente(),
            destinatario=Destinatario(),
            detalle=Detalle(),
            remesa_codigo="TEST-001",
        )
        remesa2 = Remesa(
            cliente=Cliente(),
            remitente=Remitente(),
            destinatario=Destinatario(),
            detalle=Detalle(),
            remesa_codigo="TEST-002",
        )

        payload = crear_payload_api([remesa1, remesa2])

        self.assertIsInstance(payload, dict)
        self.assertIn("remesas", payload)
        self.assertEqual(len(payload["remesas"]), 2)
        self.assertEqual(payload["remesas"][0]["remesa_codigo"], "TEST-001")
        self.assertEqual(payload["remesas"][1]["remesa_codigo"], "TEST-002")


# ============================================================================
# TESTS DEL WORKFLOW
# ============================================================================


class TestWorkflow(TestCase):
    """Tests para el workflow completo de procesamiento de guías."""

    @patch("transprensa.functions.create.clientService")
    def test_execute_guide_workflow_parametros_vacios(self, mock_client_service):
        """Test con parámetros vacíos."""
        result = execute_guide_workflow("", "")

        self.assertFalse(result["success"])
        self.assertIn("picking y bigpedido son requeridos", result["msg"])
        self.assertEqual(result["picking"], "")
        self.assertEqual(result["bigpedido"], "")

    @patch("transprensa.functions.create.clientService")
    def test_execute_guide_workflow_sin_datos_guia(self, mock_client_service):
        """Test cuando no se encuentran datos de guía."""
        mock_client_service.get_guide_data.return_value = None

        result = execute_guide_workflow("7746", "PD-103888")

        self.assertFalse(result["success"])
        self.assertIn("No se encontraron datos de guía", result["msg"])
        mock_client_service.get_guide_data.assert_called_once_with("7746", "PD-103888")

    @patch("transprensa.functions.create.mapear_guia_a_remesa")
    @patch("transprensa.functions.create.clientService")
    def test_execute_guide_workflow_error_mapeo(self, mock_client_service, mock_mapear):
        """Test cuando falla el mapeo de guía a remesa."""
        mock_client_service.get_guide_data.return_value = MOCK_GUIA_DATA
        mock_mapear.return_value = None

        result = execute_guide_workflow("7746", "PD-103888")

        self.assertFalse(result["success"])
        self.assertIn("No se pudo mapear la guía a remesa", result["msg"])

    @patch("transprensa.functions.create.threading.Thread")
    @patch("transprensa.functions.create.crear_payload_api")
    @patch("transprensa.functions.create.mapear_guia_a_remesa")
    @patch("transprensa.functions.create.clientService")
    def test_execute_guide_workflow_exitoso(
        self, mock_client_service, mock_mapear, mock_crear_payload, mock_thread
    ):
        """Test de workflow exitoso completo."""
        # Setup mocks
        mock_client_service.get_guide_data.return_value = MOCK_GUIA_DATA

        remesa_mock = Remesa(
            ciudad_codigo_origen="05001000",
            ciudad_codigo_destino="11001000",  # Ciudades diferentes
        )
        mock_mapear.return_value = remesa_mock

        mock_payload = {"remesas": [{"test": "data"}]}
        mock_crear_payload.return_value = mock_payload

        mock_client_service.create_remesas.return_value = (
            MOCK_TRANSPRENSA_CREATE_RESPONSE
        )
        mock_client_service.print_remesas.return_value = MOCK_TRANSPRENSA_PRINT_RESPONSE

        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        # Ejecutar
        result = execute_guide_workflow("7746", "PD-103888")

        # Verificar
        self.assertTrue(result["success"])
        self.assertEqual(result["picking"], "7746")
        self.assertEqual(result["bigpedido"], "PD-103888")
        self.assertEqual(result["remesa_numero"], "REM-12345")
        self.assertTrue(result["pdf_en_background"])
        self.assertIn("Guía procesada exitosamente", result["msg"])

        # Verificar que se llamó al thread para PDF
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

    @patch("transprensa.functions.create.crear_payload_api")
    @patch("transprensa.functions.create.mapear_guia_a_remesa")
    @patch("transprensa.functions.create.clientService")
    def test_execute_guide_workflow_error_crear_remesa(
        self, mock_client_service, mock_mapear, mock_crear_payload
    ):
        """Test cuando falla la creación de remesa en Transprensa."""
        mock_client_service.get_guide_data.return_value = MOCK_GUIA_DATA

        remesa_mock = Remesa(
            ciudad_codigo_origen="05001000", ciudad_codigo_destino="11001000"
        )
        mock_mapear.return_value = remesa_mock
        mock_crear_payload.return_value = {"remesas": []}

        error_response = {
            "success": False,
            "data": [{"validacion": "Error de validación"}],
            "msg": "Error en creación",
        }
        mock_client_service.create_remesas.return_value = error_response

        result = execute_guide_workflow("7746", "PD-103888")

        self.assertFalse(result["success"])
        self.assertIn("Error de validación", result["mensaje"])

    @patch("requests.get")
    def test_download_pdf_from_url_exitoso(self, mock_get):
        """Test de descarga exitosa de PDF."""
        mock_response = Mock()
        mock_response.content = b"PDF content here"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = download_pdf_from_url("https://ejemplo.com/test.pdf")

        self.assertEqual(result, b"PDF content here")
        mock_get.assert_called_once_with("https://ejemplo.com/test.pdf", timeout=10)

    @patch("requests.get")
    def test_download_pdf_from_url_error(self, mock_get):
        """Test de error en descarga de PDF."""
        mock_get.side_effect = Exception("Error de conexión")

        result = download_pdf_from_url("https://ejemplo.com/test.pdf")

        self.assertIsNone(result)

    @patch("transprensa.functions.create.download_pdf_from_url")
    @patch("transprensa.functions.create.clientService")
    def test_process_pdf_background(self, mock_client_service, mock_download):
        """Test de procesamiento de PDF en background."""
        mock_download.return_value = b"PDF content"
        mock_client_service.save_guide_pdf.return_value = {"success": True}

        # Ejecutar función
        _process_pdf_background("REM-12345", "7746", "https://ejemplo.com/test.pdf")

        # Verificar llamadas
        mock_download.assert_called_once_with(
            "https://ejemplo.com/test.pdf", timeout=10
        )
        expected_pdf_base64 = base64.b64encode(b"PDF content").decode("utf-8")
        mock_client_service.save_guide_pdf.assert_called_once_with(
            remesa_num="REM-12345", picking="7746", pdf_base64=expected_pdf_base64
        )


# ============================================================================
# TESTS DEL SERVICIO TRANSPRENSA
# ============================================================================


class TestTransprensaService(TestCase):
    """Tests para el servicio de Transprensa."""

    @patch("transprensa.services.transprensaService.TransprensaModel")
    def setUp(self, mock_model):
        """Setup para tests del servicio."""
        # Mock de la configuración
        mock_config = {
            "transprensa_config": {
                "usuario_login": "test_user",
                "usuario_password": "test_pass",
                "test": "True",
                "base_url": "https://test.transprensa.com/index.php?api=servicio.Seguridad.login",
                "token": "test_token",
                "cookie": "test_cookie",
            }
        }

        mock_repo = Mock()
        mock_repo.get_config.return_value = mock_config
        mock_repo.update_field.return_value = None  # Mock del método update_field
        mock_model.return_value = mock_repo

        self.service = TransprensaService()

    @patch("requests.Session.post")
    def test_refresh_token_exitoso(self, mock_post):
        """Test de refresh de token exitoso."""
        # Asegurar que la configuración esté cargada
        self.service._ensure_config_loaded()

        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": {"token": "new_test_token"},
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        new_token = self.service._refresh_token()

        self.assertEqual(new_token, "new_test_token")
        self.assertEqual(self.service.token, "new_test_token")

    @patch("requests.Session.post")
    def test_refresh_token_login_fallido(self, mock_post):
        """Test de refresh de token con login fallido."""
        # Asegurar que la configuración esté cargada
        self.service._ensure_config_loaded()

        mock_response = Mock()
        mock_response.json.return_value = {
            "success": False,
            "msg": "Credenciales inválidas",
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with self.assertRaises(RuntimeError) as context:
            self.service._refresh_token()

        self.assertIn("Error de login", str(context.exception))

    @patch("requests.Session.request")
    def test_request_exitoso(self, mock_request):
        """Test de request exitoso."""
        # Asegurar que la configuración esté cargada
        self.service._ensure_config_loaded()

        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "data": "test_data"}
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = self.service.request("POST", "test.endpoint", {"test": "data"})

        self.assertEqual(result, {"success": True, "data": "test_data"})

    @patch("requests.Session.request")
    @patch.object(TransprensaService, "_refresh_token")
    def test_request_con_token_expirado(self, mock_refresh, mock_request):
        """Test de request con token expirado que se renueva."""
        # Asegurar que la configuración esté cargada
        self.service._ensure_config_loaded()

        # Primera llamada: token expirado
        mock_response_expired = Mock()
        mock_response_expired.json.return_value = {
            "success": False,
            "msg": "Las credenciales de sesión han expirado",
        }
        mock_response_expired.status_code = 401
        mock_response_expired.raise_for_status.return_value = None

        # Segunda llamada: exitosa después del refresh
        mock_response_success = Mock()
        mock_response_success.json.return_value = {"success": True, "data": "test_data"}
        mock_response_success.status_code = 200
        mock_response_success.raise_for_status.return_value = None

        mock_request.side_effect = [mock_response_expired, mock_response_success]
        mock_refresh.return_value = "new_token"

        result = self.service.request("POST", "test.endpoint", {"test": "data"})

        self.assertEqual(result, {"success": True, "data": "test_data"})
        mock_refresh.assert_called_once()
        self.assertEqual(mock_request.call_count, 2)
