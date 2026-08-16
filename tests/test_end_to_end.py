def test_all_sample_change_requests(temp_context,samples):
    for sample in samples:
        result=temp_context.run_analysis(sample)
        assert result['retrieved_artefacts'] and result['rule_matches'] and result['impacted_modules']

def test_offline_behavior_no_api_fields(temp_context,samples):
    result=temp_context.run_analysis(samples[0])
    text=str(result).lower()
    assert 'api_key' not in text and 'openai' not in text and 'gemini' not in text

def test_invalid_input(temp_context):
    from src.validation import validate_change_request
    ok,errors,_=validate_change_request({'title':'','requester':'','priority':'High','description':'','reason_for_change':'','expected_behavior':''})
    assert not ok and errors

def test_evaluation_runs(temp_context):
    result=temp_context.run_evaluation()
    assert result['summary']['sample_count']==5
    assert 0 <= result['summary']['precision_at_k'] <= 1
