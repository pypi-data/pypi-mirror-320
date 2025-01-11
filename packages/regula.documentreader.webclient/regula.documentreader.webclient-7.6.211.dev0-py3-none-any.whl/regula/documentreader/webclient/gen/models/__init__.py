# coding: utf-8

# flake8: noqa
"""
    Generated by: https://openapi-generator.tech
"""

from __future__ import absolute_import

# import models into model package
from regula.documentreader.webclient.gen.models.area_array import AreaArray
from regula.documentreader.webclient.gen.models.area_container import AreaContainer
from regula.documentreader.webclient.gen.models.auth_params import AuthParams
from regula.documentreader.webclient.gen.models.authenticity_check_list import AuthenticityCheckList
from regula.documentreader.webclient.gen.models.authenticity_check_result import AuthenticityCheckResult
from regula.documentreader.webclient.gen.models.authenticity_check_result_item import AuthenticityCheckResultItem
from regula.documentreader.webclient.gen.models.authenticity_result import AuthenticityResult
from regula.documentreader.webclient.gen.models.authenticity_result_all_of import AuthenticityResultAllOf
from regula.documentreader.webclient.gen.models.authenticity_result_type import AuthenticityResultType
from regula.documentreader.webclient.gen.models.bc_pdf417_info import BcPDF417INFO
from regula.documentreader.webclient.gen.models.bc_roidetect import BcROIDETECT
from regula.documentreader.webclient.gen.models.byte_array_result import ByteArrayResult
from regula.documentreader.webclient.gen.models.byte_array_result_all_of import ByteArrayResultAllOf
from regula.documentreader.webclient.gen.models.check_diagnose import CheckDiagnose
from regula.documentreader.webclient.gen.models.check_result import CheckResult
from regula.documentreader.webclient.gen.models.chosen_document_type import ChosenDocumentType
from regula.documentreader.webclient.gen.models.chosen_document_type_result import ChosenDocumentTypeResult
from regula.documentreader.webclient.gen.models.chosen_document_type_result_all_of import ChosenDocumentTypeResultAllOf
from regula.documentreader.webclient.gen.models.container_list import ContainerList
from regula.documentreader.webclient.gen.models.critical import Critical
from regula.documentreader.webclient.gen.models.cross_source_value_comparison import CrossSourceValueComparison
from regula.documentreader.webclient.gen.models.data_module import DataModule
from regula.documentreader.webclient.gen.models.details_optical import DetailsOptical
from regula.documentreader.webclient.gen.models.details_rfid import DetailsRFID
from regula.documentreader.webclient.gen.models.device_info import DeviceInfo
from regula.documentreader.webclient.gen.models.doc_bar_code_info import DocBarCodeInfo
from regula.documentreader.webclient.gen.models.doc_bar_code_info_all_of import DocBarCodeInfoAllOf
from regula.documentreader.webclient.gen.models.doc_bar_code_info_fields_list import DocBarCodeInfoFieldsList
from regula.documentreader.webclient.gen.models.doc_visual_extended_field import DocVisualExtendedField
from regula.documentreader.webclient.gen.models.doc_visual_extended_info import DocVisualExtendedInfo
from regula.documentreader.webclient.gen.models.document_format import DocumentFormat
from regula.documentreader.webclient.gen.models.document_image import DocumentImage
from regula.documentreader.webclient.gen.models.document_image_result import DocumentImageResult
from regula.documentreader.webclient.gen.models.document_image_result_all_of import DocumentImageResultAllOf
from regula.documentreader.webclient.gen.models.document_position import DocumentPosition
from regula.documentreader.webclient.gen.models.document_position_result import DocumentPositionResult
from regula.documentreader.webclient.gen.models.document_position_result_all_of import DocumentPositionResultAllOf
from regula.documentreader.webclient.gen.models.document_type import DocumentType
from regula.documentreader.webclient.gen.models.document_type_recognition_result import DocumentTypeRecognitionResult
from regula.documentreader.webclient.gen.models.document_types_candidates import DocumentTypesCandidates
from regula.documentreader.webclient.gen.models.document_types_candidates_list import DocumentTypesCandidatesList
from regula.documentreader.webclient.gen.models.document_types_candidates_result import DocumentTypesCandidatesResult
from regula.documentreader.webclient.gen.models.document_types_candidates_result_all_of import DocumentTypesCandidatesResultAllOf
from regula.documentreader.webclient.gen.models.documents_database import DocumentsDatabase
from regula.documentreader.webclient.gen.models.encrypted_rcl_result import EncryptedRCLResult
from regula.documentreader.webclient.gen.models.encrypted_rcl_result_all_of import EncryptedRCLResultAllOf
from regula.documentreader.webclient.gen.models.fdsid_list import FDSIDList
from regula.documentreader.webclient.gen.models.face_api import FaceApi
from regula.documentreader.webclient.gen.models.face_api_search import FaceApiSearch
from regula.documentreader.webclient.gen.models.fiber_result import FiberResult
from regula.documentreader.webclient.gen.models.fiber_result_all_of import FiberResultAllOf
from regula.documentreader.webclient.gen.models.get_transactions_by_tag_response import GetTransactionsByTagResponse
from regula.documentreader.webclient.gen.models.graphic_field import GraphicField
from regula.documentreader.webclient.gen.models.graphic_field_type import GraphicFieldType
from regula.documentreader.webclient.gen.models.graphic_fields_list import GraphicFieldsList
from regula.documentreader.webclient.gen.models.graphics_result import GraphicsResult
from regula.documentreader.webclient.gen.models.graphics_result_all_of import GraphicsResultAllOf
from regula.documentreader.webclient.gen.models.healthcheck import Healthcheck
from regula.documentreader.webclient.gen.models.healthcheck_documents_database import HealthcheckDocumentsDatabase
from regula.documentreader.webclient.gen.models.ident_result import IdentResult
from regula.documentreader.webclient.gen.models.ident_result_all_of import IdentResultAllOf
from regula.documentreader.webclient.gen.models.image_data import ImageData
from regula.documentreader.webclient.gen.models.image_qa import ImageQA
from regula.documentreader.webclient.gen.models.image_quality_check import ImageQualityCheck
from regula.documentreader.webclient.gen.models.image_quality_check_list import ImageQualityCheckList
from regula.documentreader.webclient.gen.models.image_quality_check_type import ImageQualityCheckType
from regula.documentreader.webclient.gen.models.image_quality_result import ImageQualityResult
from regula.documentreader.webclient.gen.models.image_quality_result_all_of import ImageQualityResultAllOf
from regula.documentreader.webclient.gen.models.image_transaction_data import ImageTransactionData
from regula.documentreader.webclient.gen.models.images import Images
from regula.documentreader.webclient.gen.models.images_available_source import ImagesAvailableSource
from regula.documentreader.webclient.gen.models.images_field import ImagesField
from regula.documentreader.webclient.gen.models.images_field_value import ImagesFieldValue
from regula.documentreader.webclient.gen.models.images_result import ImagesResult
from regula.documentreader.webclient.gen.models.images_result_all_of import ImagesResultAllOf
from regula.documentreader.webclient.gen.models.in_data import InData
from regula.documentreader.webclient.gen.models.in_data_transaction_images_field_value import InDataTransactionImagesFieldValue
from regula.documentreader.webclient.gen.models.in_data_video import InDataVideo
from regula.documentreader.webclient.gen.models.inline_response200 import InlineResponse200
from regula.documentreader.webclient.gen.models.inline_response2001 import InlineResponse2001
from regula.documentreader.webclient.gen.models.lcid import LCID
from regula.documentreader.webclient.gen.models.lexical_analysis_result import LexicalAnalysisResult
from regula.documentreader.webclient.gen.models.lexical_analysis_result_all_of import LexicalAnalysisResultAllOf
from regula.documentreader.webclient.gen.models.license_result import LicenseResult
from regula.documentreader.webclient.gen.models.license_result_all_of import LicenseResultAllOf
from regula.documentreader.webclient.gen.models.light import Light
from regula.documentreader.webclient.gen.models.list_transactions_by_tag_response import ListTransactionsByTagResponse
from regula.documentreader.webclient.gen.models.list_verified_fields import ListVerifiedFields
from regula.documentreader.webclient.gen.models.liveness_params import LivenessParams
from regula.documentreader.webclient.gen.models.log_level import LogLevel
from regula.documentreader.webclient.gen.models.mrz_format import MRZFormat
from regula.documentreader.webclient.gen.models.measure_system import MeasureSystem
from regula.documentreader.webclient.gen.models.mrz_detect_mode_enum import MrzDetectModeEnum
from regula.documentreader.webclient.gen.models.ocr_security_text_result import OCRSecurityTextResult
from regula.documentreader.webclient.gen.models.ocr_security_text_result_all_of import OCRSecurityTextResultAllOf
from regula.documentreader.webclient.gen.models.one_candidate import OneCandidate
from regula.documentreader.webclient.gen.models.original_symbol import OriginalSymbol
from regula.documentreader.webclient.gen.models.out_data import OutData
from regula.documentreader.webclient.gen.models.out_data_transaction_images_field_value import OutDataTransactionImagesFieldValue
from regula.documentreader.webclient.gen.models.p_array_field import PArrayField
from regula.documentreader.webclient.gen.models.parsing_notification_codes import ParsingNotificationCodes
from regula.documentreader.webclient.gen.models.per_document_config import PerDocumentConfig
from regula.documentreader.webclient.gen.models.photo_ident_result import PhotoIdentResult
from regula.documentreader.webclient.gen.models.photo_ident_result_all_of import PhotoIdentResultAllOf
from regula.documentreader.webclient.gen.models.point import Point
from regula.documentreader.webclient.gen.models.point_array import PointArray
from regula.documentreader.webclient.gen.models.points_container import PointsContainer
from regula.documentreader.webclient.gen.models.process_params import ProcessParams
from regula.documentreader.webclient.gen.models.process_params_rfid import ProcessParamsRfid
from regula.documentreader.webclient.gen.models.process_request import ProcessRequest
from regula.documentreader.webclient.gen.models.process_request_image import ProcessRequestImage
from regula.documentreader.webclient.gen.models.process_response import ProcessResponse
from regula.documentreader.webclient.gen.models.process_system_info import ProcessSystemInfo
from regula.documentreader.webclient.gen.models.processing_status import ProcessingStatus
from regula.documentreader.webclient.gen.models.raw_image_container_list import RawImageContainerList
from regula.documentreader.webclient.gen.models.rectangle_coordinates import RectangleCoordinates
from regula.documentreader.webclient.gen.models.result import Result
from regula.documentreader.webclient.gen.models.result_item import ResultItem
from regula.documentreader.webclient.gen.models.rfid_location import RfidLocation
from regula.documentreader.webclient.gen.models.rfid_origin import RfidOrigin
from regula.documentreader.webclient.gen.models.scenario import Scenario
from regula.documentreader.webclient.gen.models.security_feature_result import SecurityFeatureResult
from regula.documentreader.webclient.gen.models.security_feature_result_all_of import SecurityFeatureResultAllOf
from regula.documentreader.webclient.gen.models.security_feature_type import SecurityFeatureType
from regula.documentreader.webclient.gen.models.source import Source
from regula.documentreader.webclient.gen.models.source_validity import SourceValidity
from regula.documentreader.webclient.gen.models.status import Status
from regula.documentreader.webclient.gen.models.status_result import StatusResult
from regula.documentreader.webclient.gen.models.status_result_all_of import StatusResultAllOf
from regula.documentreader.webclient.gen.models.string_recognition_result import StringRecognitionResult
from regula.documentreader.webclient.gen.models.symbol_candidate import SymbolCandidate
from regula.documentreader.webclient.gen.models.symbol_recognition_result import SymbolRecognitionResult
from regula.documentreader.webclient.gen.models.text import Text
from regula.documentreader.webclient.gen.models.text_available_source import TextAvailableSource
from regula.documentreader.webclient.gen.models.text_data_result import TextDataResult
from regula.documentreader.webclient.gen.models.text_data_result_all_of import TextDataResultAllOf
from regula.documentreader.webclient.gen.models.text_field import TextField
from regula.documentreader.webclient.gen.models.text_field_type import TextFieldType
from regula.documentreader.webclient.gen.models.text_field_value import TextFieldValue
from regula.documentreader.webclient.gen.models.text_post_processing import TextPostProcessing
from regula.documentreader.webclient.gen.models.text_result import TextResult
from regula.documentreader.webclient.gen.models.text_result_all_of import TextResultAllOf
from regula.documentreader.webclient.gen.models.transaction_image import TransactionImage
from regula.documentreader.webclient.gen.models.transaction_info import TransactionInfo
from regula.documentreader.webclient.gen.models.transaction_process_get_response import TransactionProcessGetResponse
from regula.documentreader.webclient.gen.models.transaction_process_request import TransactionProcessRequest
from regula.documentreader.webclient.gen.models.verification_result import VerificationResult
from regula.documentreader.webclient.gen.models.verified_field_map import VerifiedFieldMap
from regula.documentreader.webclient.gen.models.visibility import Visibility
