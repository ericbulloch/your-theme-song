from flask import Flask, send_from_directory


app = Flask(__name__)


@app.route('/music/<filename>')
def get_audio(filename):
	return send_from_directory('music', filename)


if __name__ == '__main__':
	app.run(debug=True)