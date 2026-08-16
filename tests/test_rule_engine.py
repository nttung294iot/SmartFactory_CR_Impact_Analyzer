def test_rule_matching_emergency(temp_context):
    prep=temp_context.preprocessor.process("cảnh báo nhiệt độ critical vượt ngưỡng 15 phút tự động tạo Emergency Work Order")
    matches=temp_context.rule_engine.match(prep,threshold=0.2)
    assert any(x['category']=='Emergency Work Order' for x in matches)

def test_multiple_rule_matching(temp_context):
    prep=temp_context.preprocessor.process("Work Order chưa tiếp nhận sau 30 phút phải escalation đến Maintenance Manager")
    matches=temp_context.rule_engine.match(prep,threshold=0.2)
    assert len(matches) >= 2

def test_generic_fallback(temp_context):
    prep=temp_context.preprocessor.process("hỗ trợ ý tưởng chưa xác định điều kiện")
    matches=temp_context.rule_engine.match(prep,threshold=0.8)
    assert matches[0]['is_fallback']

def test_required_keyword_blocks_rule(temp_context):
    rule=next(x for x in temp_context.rules if x['id']=='RULE-WO-003')
    prep=temp_context.preprocessor.process("Work Order ưu tiên cao theo vai trò")
    tested=temp_context.rule_engine.test_rule(rule,prep)
    assert tested.get('match_score',0) == 0 or tested.get('is_fallback')
