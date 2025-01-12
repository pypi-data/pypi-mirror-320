from lumbni_client.response import LumbniApiResponse

def test_is_successful():
    response = {
        "status": "success",
        "message": "Text generated successfully",
        "data": {}
    }
    api_response = LumbniApiResponse(response)
    assert api_response.is_successful() is True

def test_get_generated_text():
    response = {
        "status": "success",
        "message": "Text generated successfully",
        "data": {
            "outputs": [{"message": {"content": "Here is a joke!"}}]
        }
    }
    api_response = LumbniApiResponse(response)
    assert api_response.get_generated_text() == "Here is a joke!"
