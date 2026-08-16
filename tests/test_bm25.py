def test_bm25_ranking_temperature(temp_context):
    prep=temp_context.preprocessor.process("nhiệt độ vượt ngưỡng máy CNC 15 phút tạo phiếu bảo trì khẩn cấp")
    result=temp_context.retriever.retrieve(prep,top_k=10)
    ids=[x['document_id'] for x in result]
    assert any(x in ids for x in ['BR-MON-001','TC-MON-001','US-MON-001'])

def test_top_k(temp_context):
    prep=temp_context.preprocessor.process("work order alert")
    assert len(temp_context.retriever.retrieve(prep,top_k=3)) == 3

def test_metadata_type_filter(temp_context):
    prep=temp_context.preprocessor.process("work order")
    result=temp_context.retriever.retrieve(prep,top_k=10,artefact_types=['business_rule'])
    assert result and all(x['artefact_type']=='business_rule' for x in result)

def test_metadata_module_filter(temp_context):
    prep=temp_context.preprocessor.process("preventive maintenance runtime")
    result=temp_context.retriever.retrieve(prep,top_k=10,module_ids=['MOD-PM'])
    assert result and all('MOD-PM' in x['module_ids'] for x in result)

def test_bm25_score_not_probability(temp_context):
    prep=temp_context.preprocessor.process("work order")
    result=temp_context.retriever.retrieve(prep,top_k=3)
    assert any(x['bm25_score'] > 1 for x in result)
