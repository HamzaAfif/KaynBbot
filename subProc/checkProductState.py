def check_if_adding_product(session):
    
    current_state = session.get_state()
    return current_state in ['adding_product', 'updating_product']