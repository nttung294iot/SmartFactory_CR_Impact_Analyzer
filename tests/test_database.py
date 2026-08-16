def test_database_save_load_cr(temp_context,samples):
    temp_context.database.save_change_request(samples[0])
    assert temp_context.database.get_change_request('CR-001')['title']=='Cảnh báo nhiệt độ thiết bị'

def test_database_save_load_analysis(temp_context,samples):
    result=temp_context.run_analysis(samples[1])
    assert temp_context.database.get_analysis(result['analysis_id'])['cr_id']=='CR-002'

def test_review_save(temp_context,samples):
    result=temp_context.run_analysis(samples[0])
    temp_context.database.save_review(result['analysis_id'],'BA Tester','Confirmed','Ổn',{})
    assert temp_context.database.list_reviews(result['analysis_id'])[0]['review_status']=='Confirmed'

def test_duplicate_id_upsert(temp_context,samples):
    temp_context.database.save_change_request(samples[0]); updated=dict(samples[0]); updated['title']='Updated'; temp_context.database.save_change_request(updated)
    assert temp_context.database.get_change_request('CR-001')['title']=='Updated'
