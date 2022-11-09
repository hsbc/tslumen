import mock
from tslumen.scheduling import TqdmParallel, Scheduler, delayed


def test_tqdmparallel():
    with mock.patch('tslumen.scheduling.Parallel', autospec=True) as parallel:
        tq1 = TqdmParallel(n_jobs=53, progress_disable=True)
        assert tq1.progress_disable is True
        assert tq1.n_jobs == 53
        parallel.assert_not_called()
        tq1('fun', 'args')
        parallel.assert_called_with(tq1, 'fun', 'args')

    tq2 = TqdmParallel(n_jobs=1, prefer='processes')
    res = tq2((delayed(lambda x: x+1)(n,) for n in range(10)))
    assert sorted(res) == list(range(1,11))


def test_scheduler():
    s1 = Scheduler()
    s2 = Scheduler({'n_jobs': 81})
    c = Scheduler.Config()
    c.n_jobs = 44
    s3 = Scheduler(c)

    assert s1.config['n_jobs'] == Scheduler.Config().n_jobs
    assert s2.config['n_jobs'] == 81
    assert s3.config['n_jobs'] == 44


    s = Scheduler({'n_jobs': 1, 'prefer': 'threads'})
    res = s.run(lambda x: x + 1, [(n,) for n in range(10)])
    assert sorted(res) == list(range(1, 11))
