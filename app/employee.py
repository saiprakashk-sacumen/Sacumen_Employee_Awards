from flask import Flask, request, jsonify, send_file
import pandas as pd
import io

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_json_to_csv():
    try:
        import json
        raw_data = request.data  # raw bytes
        data = json.loads(raw_data)  # convert to Python list/dict

        # Flatten nested JSON
        df = pd.json_normalize(data)

        # Save CSV to buffer
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='employees.csv'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 400



if __name__ == '__main__':
    app.run(debug=True, port=5000)
