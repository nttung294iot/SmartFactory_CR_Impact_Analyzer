def test_impact_module_mapping(temp_context,samples):
    result=temp_context.run_analysis(samples[0])
    ids={x['module_id'] for x in result['impacted_modules']}
    assert {'MOD-MON','MOD-WO'}.intersection(ids)

def test_risk_generation(temp_context,samples):
    result=temp_context.run_analysis(samples[1])
    assert result['risks']

def test_question_generation(temp_context,samples):
    result=temp_context.run_analysis(samples[2])
    assert result['clarifying_questions']

def test_user_story_template(temp_context,samples):
    result=temp_context.run_analysis(samples[0])
    assert result['draft_user_stories'][0]['user_story'].startswith('As a')

def test_business_rule_template(temp_context,samples):
    result=temp_context.run_analysis(samples[2])
    assert result['draft_business_rules'][0]['business_rule'].startswith('DRAFT-BR-')

def test_test_scenario_template(temp_context,samples):
    result=temp_context.run_analysis(samples[2])
    assert result['draft_test_scenarios'][0]['expected_result']
