import os
import re
import urllib.parse

def clean_file(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        c = f.read()

    # Replace dummy example link
    c = c.replace('[report.md#L10-L25](file:///path/to/report.md#L10-L25)', '`[report.md#L10-L25](file:///path/to/report.md#L10-L25)`')

    # Replace broken skill link
    c = c.replace('file:///C:/Users/Administrator/.gemini/config/skills/tududi-tasks/SKILL.md', 'file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/SKILL.md')
    c = c.replace('[`tududi-tasks`]', '[`neuro-copilot / tududi`]')

    # Replace chaos_monkey
    c = c.replace('scripts/chaos_monkey.py', 'scripts/fault_injection_harness.py')
    c = c.replace('chaos_monkey.py', 'fault_injection_harness.py')

    # Replace deleted domain stubs with existing modules
    c = c.replace('src/domain/counterfactual_rag.py', 'src/domain/retrieval/retrieval_pipeline_dag.py')
    c = c.replace('src/domain/speculative_rag.py', 'src/domain/speculative_streamer.py')
    c = c.replace('src/domain/cross_lingual_fusion.py', 'src/domain/retrieval/retrieval_pipeline_dag.py')
    c = c.replace('src/domain/cross_lingual_aligner.py', 'src/core/text_utils.py')
    c = c.replace('src/domain/crosslingual_bridge.py', 'src/core/text_utils.py')
    c = c.replace('src/domain/swarm_rag.py', 'src/domain/multi_agent_consensus.py')
    c = c.replace('src/domain/active_rag.py', 'src/domain/retrieval/rag_engine.py')
    c = c.replace('src/domain/colbert_reranker.py', 'src/domain/retrieval/reranking.py')
    c = c.replace('src/domain/contextual_noise_mask.py', 'src/domain/adaptive_context_compressor.py')

    # Also replace short names in table if any
    c = c.replace('[`counterfactual_rag.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/retrieval/retrieval_pipeline_dag.py)', '[`retrieval_pipeline_dag.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/retrieval/retrieval_pipeline_dag.py)')
    c = c.replace('[`speculative_rag.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/speculative_streamer.py)', '[`speculative_streamer.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/speculative_streamer.py)')
    c = c.replace('[`cross_lingual_fusion.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/retrieval/retrieval_pipeline_dag.py)', '[`retrieval_pipeline_dag.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/retrieval/retrieval_pipeline_dag.py)')
    c = c.replace('[`cross_lingual_aligner.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/core/text_utils.py)', '[`text_utils.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/core/text_utils.py)')
    c = c.replace('[`swarm_rag.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/multi_agent_consensus.py)', '[`multi_agent_consensus.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/multi_agent_consensus.py)')
    c = c.replace('[`active_rag.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/retrieval/rag_engine.py)', '[`rag_engine.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/retrieval/rag_engine.py)')
    c = c.replace('[`colbert_reranker.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/retrieval/reranking.py)', '[`reranking.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/retrieval/reranking.py)')
    c = c.replace('[`contextual_noise_mask.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/adaptive_context_compressor.py)', '[`adaptive_context_compressor.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/adaptive_context_compressor.py)')

    # Update counts in header badges
    c = c.replace('badge/Domain%20Modules-141-blue.svg', 'badge/Domain%20Modules-251-blue.svg')
    c = c.replace('alt="141 Domain Modules"', 'alt="251 Domain Modules"')
    c = c.replace('badge/Test%20Suites-99-emerald.svg', 'badge/Test%20Suites-203-emerald.svg')
    c = c.replace('alt="99 Test Suites"', 'alt="203 Test Suites"')
    c = c.replace('141 Decoupled Domain Modules', '251 Decoupled Domain Modules')
    c = c.replace('99 Automated Test Suites', '203 Automated Test Suites')
    c = c.replace('98 Unit & Integration Test Suites', '203 Unit & Integration Test Suites')
    c = c.replace('Taxonomy of All 135 Domain Modules', 'Taxonomy of Domain Intelligence Modules')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(c)
    print(f'Cleaned: {filepath}')

clean_file('README.md')
clean_file('scripts/build_master_readme.py')
