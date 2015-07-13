import logging
import subprocess
import sys

import workflow
import pepper
import pepper.cli

logger = logging.getLogger(__name__)


def run_alfred(query):
    """Call Alfred with ``query``"""
    subprocess.call([
        'osascript', '-e',
        'tell application "Alfred 2" to search "{}"'.format(query)])


def redirect(wf):
    args = wf.args
    args.remove('redirect')
    run_alfred('salt ' + ' '.join(args))


def salt(func):
    def wrapper(wf, *args, **kwargs):
        try:
            cli = pepper.cli.PepperCli()
            cli.parse()
            opts = cli.get_login_details()
            api = pepper.Pepper(opts['SALTAPI_URL'])
            api.login(opts['SALTAPI_USER'], opts['SALTAPI_PASS'], opts['SALTAPI_EAUTH'])
            kwargs['api'] = api
        except pepper.PepperException, e:
            wf.add_item('Salt Exception', str(e))
            wf.send_feedback()
        else:
            return func(wf, *args, **kwargs)
    return wrapper


@salt
def jobs(wf, api):
    for result in api.runner('jobs.list_jobs').get('return', []):
        for jid, jout in result.iteritems():
            wf.logger.debug('%s', jout)
            wf.add_item(jid, jout['Function'], arg='showjob' + jid, valid=True)
    wf.send_feedback()


@salt
def ping(wf, api):
    cli = PepperCli()
    cli.parse()
    opts = cli.get_login_details()
    api = Pepper(opts['SALTAPI_URL'])
    api.login(opts['SALTAPI_USER'], opts['SALTAPI_PASS'], opts['SALTAPI_EAUTH'])


def main(wf):
    if 'redirect' in wf.args:
        return redirect(wf)
    if 'jobs' in wf.args:
        return jobs(wf)
    wf.add_item('Unknown Command')
    wf.add_item('List Jobs', arg='redirect jobs', valid=True)
    wf.send_feedback()

if __name__ == '__main__':
    sys.exit(main(workflow.Workflow()))
