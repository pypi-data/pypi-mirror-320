from app_opt import app  

def test_home_route():
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
        assert b"<p>Processing your video... Please wait.</p>" in response.data 

# test_home_route()
