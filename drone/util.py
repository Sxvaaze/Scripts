def get_motion(similarity_percentage: float):
    """Αν η ομοιότητα μεταξύ 2 εικόνων είναι μικρότερη του 95%, τότε μπορούμε με σιγουριά να γυρίσουμε πως υπήρξε κίνηση"""
    return similarity_percentage < 95