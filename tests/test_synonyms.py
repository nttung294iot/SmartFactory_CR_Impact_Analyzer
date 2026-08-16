def test_vietnamese_synonym(temp_context):
    result=temp_context.preprocessor.process("báo cấp trên")
    assert "escalation" in result.expanded_tokens

def test_english_synonym(temp_context):
    result=temp_context.preprocessor.process("maintenance order")
    assert "work_order" in result.expanded_tokens

def test_synonym_disabled_behavior(temp_context):
    result=temp_context.preprocessor.process("phiếu bảo trì",synonym_expansion=False,phrase_normalization=False)
    assert "work_order" not in result.expanded_tokens

def test_dictionary_size(temp_context):
    assert len(temp_context.synonyms) >= 30
