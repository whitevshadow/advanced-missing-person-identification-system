import pytest
from app.services.matching_service import calculate_similarity


def test_calculate_similarity_identical():
    """Test similarity calculation for identical embeddings."""
    embedding1 = [1.0, 0.0, 0.0, 0.0]
    embedding2 = [1.0, 0.0, 0.0, 0.0]
    
    similarity = calculate_similarity(embedding1, embedding2)
    assert 0.0 <= similarity <= 1.0
    assert similarity > 0.95  # Should be very high for identical


def test_calculate_similarity_different():
    """Test similarity calculation for different embeddings."""
    embedding1 = [1.0, 0.0, 0.0, 0.0]
    embedding2 = [0.0, 1.0, 0.0, 0.0]
    
    similarity = calculate_similarity(embedding1, embedding2)
    assert 0.0 <= similarity <= 1.0


def test_calculate_similarity_range():
    """Test that similarity is always in valid range."""
    embeddings = [
        [1.0, 0.0, 0.0],
        [0.5, 0.5, 0.0],
        [0.0, 0.0, 1.0],
    ]
    
    for i in range(len(embeddings)):
        for j in range(len(embeddings)):
            similarity = calculate_similarity(embeddings[i], embeddings[j])
            assert 0.0 <= similarity <= 1.0


def test_similarity_symmetry():
    """Test that similarity is symmetric: sim(A,B) == sim(B,A)."""
    embedding1 = [1.0, 0.5, 0.2]
    embedding2 = [0.8, 0.3, 0.4]
    
    sim_12 = calculate_similarity(embedding1, embedding2)
    sim_21 = calculate_similarity(embedding2, embedding1)
    
    assert abs(sim_12 - sim_21) < 0.0001  # Allow small floating point error


def test_similarity_self():
    """Test that similarity of embedding with itself is 1.0."""
    embedding = [1.0, 0.5, 0.3, 0.2]
    
    similarity = calculate_similarity(embedding, embedding)
    assert abs(similarity - 1.0) < 0.0001


def test_empty_embeddings():
    """Test handling of empty embeddings."""
    try:
        similarity = calculate_similarity([], [])
        # If it doesn't raise, just check the result is valid
        assert 0.0 <= similarity <= 1.0
    except (ValueError, ZeroDivisionError):
        # This is also acceptable behavior
        pass
