import tempfile
import pandas as pd
from flask import request, Response, json, Blueprint, send_file

tests = Blueprint("tests", __name__)

@tests.route("/", methods=["GET"])
def handle_test_home():
    try:
        return Response(
            response=json.dumps({"status": "running-test-home"}),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return Response(
            response=json.dumps(
                {"status": "failed", "message": str(e), "error": str(e)}
            ),
            status=500,
            mimetype="application/json",
        )


@tests.route("/test-1", methods=["GET"])
def handle_test_1():
    try:
        return Response(
            response=json.dumps({"status": "running-test-1"}),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return Response(
            response=json.dumps(
                {"status": "failed", "message": str(e), "error": str(e)}
            ),
            status=500,
            mimetype="application/json",
        )

@tests.route("/test-io", methods=["POST"])
def handle_test_io():
    """"""
    try:
        file_test = request.files.get("file_test")
        tempfile_path_test = tempfile.NamedTemporaryFile().name
        file_test.save(tempfile_path_test)
        df = pd.read_csv(tempfile_path_test)
        print(list(df.columns))
        return send_file(tempfile_path_test, mimetype="csv", as_attachment="True")
    except Exception as e:
        return Response(
            response=json.dumps(
                {"status": "failed", "message": str(e), "error": str(e)}
            ),
            status=500,
            mimetype="application/json",
        )
