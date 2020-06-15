from rest_framework.exceptions import APIException

class WrongInputData(APIException):
    status_code = 400
    default_detail = 'Wrong Input data provided. the objectID1 as an identifier'
