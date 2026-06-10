OPENAI_API_KEY='sk-proj-1234567890abcdef1234567890abcdef'\n\ndef get_user_data(user_id):\n    # 懒得写校验了，直接拼SQL吧\n    query = f'SELECT * FROM users WHERE id = {user_id}'\n    db.execute(query)
