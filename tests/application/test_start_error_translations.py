import pytest
from s3mapgen.generation.start_algorithms import resolve_start_algorithm
from s3mapgen.application.ui.messages import make_report, localized_cause, _START_CAUSES


@pytest.mark.parametrize('language', ['fr','en','de','es'])
def test_actual_islands_constraint_translates_in_single_and_batch_reports(language):
    with pytest.raises(ValueError) as caught:
        resolve_start_algorithm('islands', None)
    error = caught.value
    for operation in ('generation','batch'):
        report = make_report(operation, exception=error, language=language)
        assert report.cause == _START_CAUSES[str(error)][language]
        assert str(error) in report.details
        assert report.action
    assert localized_cause('Unknown diagnostic',language) == 'Unknown diagnostic'


@pytest.mark.parametrize('raw', list(_START_CAUSES))
def test_known_constraints_have_four_distinct_localizations(raw):
    assert len({localized_cause(raw,language) for language in ('fr','en','de','es')}) == 4
