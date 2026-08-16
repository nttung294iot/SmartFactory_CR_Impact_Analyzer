def test_unicode_normalization(temp_context):
    result=temp_context.preprocessor.process("NHIỆT ĐỘ   máy CNC")
    assert "temperature" in result.expanded_tokens

def test_phrase_normalization(temp_context):
    result=temp_context.preprocessor.process("phiếu bảo trì khẩn cấp")
    assert "work_order" in result.normalized_text

def test_duration_detection(temp_context):
    result=temp_context.preprocessor.process("liên tục 15 phút và sau 2 giờ")
    assert any("15" in x for x in result.detected_durations)
    assert any("2" in x for x in result.detected_durations)

def test_priority_detection(temp_context):
    result=temp_context.preprocessor.process("Work Order P1 mức ưu tiên High")
    assert any(p in result.detected_priorities for p in ["High", "Critical", "P1"])

def test_role_and_equipment_detection(temp_context):
    result=temp_context.preprocessor.process("Maintenance Manager kiểm tra máy CNC")
    assert "Maintenance Manager" in result.detected_roles
    assert "Máy CNC" in result.detected_equipment
