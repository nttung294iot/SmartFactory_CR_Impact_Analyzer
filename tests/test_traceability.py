def test_rtm_generation(temp_context,samples):
    result=temp_context.run_analysis(samples[0])
    assert result['traceability_matrix']
    assert {'cr_id','rule_id','module_id','test_case_id'}.issubset(result['traceability_matrix'][0])

def test_generic_rtm(temp_context,samples):
    temp_context.database.upsert_setting('rule_threshold',0.95); temp_context.refresh()
    result=temp_context.run_analysis(samples[4])
    assert result['traceability_matrix'][0]['review_status']=='Draft'
