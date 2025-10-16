from app.utils.distance import haversine_distance


def test_haversine_same_location():
    """Test distance between same coordinates is zero"""
    distance = haversine_distance(40.7128, -74.0060, 40.7128, -74.0060)
    assert distance == 0.0


def test_haversine_known_distance():
    """Test distance between NYC and Philadelphia (approximately 130 km)"""
    # NYC coordinates
    nyc_lat, nyc_lng = 40.7128, -74.0060
    # Philadelphia coordinates
    philly_lat, philly_lng = 39.9526, -75.1652

    distance = haversine_distance(nyc_lat, nyc_lng, philly_lat, philly_lng)

    # Distance should be approximately 130 km (allow 10% margin)
    assert 120 <= distance <= 140


def test_haversine_short_distance():
    """Test short distance within NYC (Times Square to Central Park)"""
    # Times Square
    ts_lat, ts_lng = 40.7580, -73.9855
    # Central Park
    cp_lat, cp_lng = 40.7829, -73.9654

    distance = haversine_distance(ts_lat, ts_lng, cp_lat, cp_lng)

    # Distance should be approximately 3-4 km
    assert 2 <= distance <= 5


def test_haversine_symmetry():
    """Test that distance from A to B equals distance from B to A"""
    lat1, lng1 = 40.7128, -74.0060
    lat2, lng2 = 40.7589, -73.9851

    distance1 = haversine_distance(lat1, lng1, lat2, lng2)
    distance2 = haversine_distance(lat2, lng2, lat1, lng1)

    assert distance1 == distance2
