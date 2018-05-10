# coding:utf-8
import os
import re
import stat
import mimetypes
from math import log
from datetime import datetime


from flask import Flask, request, jsonify, abort, Response, send_file
from werkzeug.utils import secure_filename


ROOT_DIR = '/tmp'
app = Flask(__name__)


def get_type(mode):
    if stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
        return 'dir'
    return 'file'


def pretty_size(n, pow=0, b=1024, u='B'):
    pre = [''] + [p + '' for p in 'KMGTPEZY']
    pow, n = min(int(log(max(n*b**pow, 1), b)),
                  len(pre)-1), n*b**pow
    return "%%.%if%%s%%s" % abs(
        pow % (-pow-1)) % (n/b**float(pow), pre[pow], u)


def pretty_time(timestamp):
    mdate = datetime.utcfromtimestamp(timestamp)
    return datetime.strftime(mdate, "%Y-%m-%d %H:%M:%S")


def partial_response(path, start, end=None):
    file_size = os.path.getsize(path)

    if end is None:
        end = file_size - start - 1
    end = min(end, file_size - 1)
    length = end - start + 1

    with open(path, 'rb') as fd:
        fd.seek(start)
        bytess = fd.read(length)
    assert len(bytess) == length

    response = Response(
        bytes,
        206,
        mimetype=mimetypes.guess_type(path)[0],
        direct_passthrough=True,
    )
    response.headers.add(
        'Content-Range', 'bytes {0}-{1}/{2}'.format(
            start, end, file_size,
        ),
    )
    response.headers.add(
        'Accept-Ranges', 'bytes'
    )
    return response


def get_range(request):
    ranges = request.headers.get('Range')
    m = re.match('bytes=(?P<start>\d+)-(?P<end>\d+)?', ranges)
    if m:
        start = m.group('start')
        end = m.group('end')
        start = int(start)
        if end is not None:
            end = int(end)
        return start, end
    else:
        return 0, None


@app.route("/", methods=['POST'])
@app.route("/<path:p>", methods=['POST'])
def upload_handler(p=''):
    path = os.path.join(ROOT_DIR, p)
    info = {'code': 1}
    if os.path.isdir(path):
        f = request.files.get('file')
        try:
            filename = secure_filename(f.filename)
            f.save(os.path.join(path, filename))
        except Exception as e:
            info['msg'] = str(e)
        else:
            info['code'] = 0
            info['msg'] = 'File Saved'
    else:
        info['msg'] = 'Invalid Operation'
    return jsonify(info)


@app.route("/", methods=["GET"])
@app.route("/<path:p>", methods=["GET"])
def download_handler(p=''):
    path = os.path.join(ROOT_DIR, p)
    if os.path.isdir(path):
        contents = []
        for filename in os.listdir(path):
            filepath = os.path.join(path, filename)
            stat_res = os.stat(filepath)
            contents.append('  '.join([
                get_type(stat_res.st_mode),
                pretty_time(stat_res.st_mtime),
                pretty_size(stat_res.st_size),
                filename,
            ]))
        return '\n'.join(contents) + '\n'
    elif os.path.isfile(path):
        if 'Range' in request.headers:
            start, end = get_range(request)
            res = partial_response(path, start, end)
        else:
            res = send_file(path)
            res.headers.add('Content-Disposition', 'attachment')
    else:
        abort(404)
    return res


def main():
    app.run('0.0.0.0', 8080, debug=True)


if __name__ == "__main__":
    main()


