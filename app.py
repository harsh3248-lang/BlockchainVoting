from flask import Flask, render_template, request, redirect, url_for, session

from blockchain import Blockchain
import database


app = Flask(__name__)

app.secret_key = "college-voting-secret-key"


# =========================================================
# BLOCKCHAIN
# =========================================================

blockchain = Blockchain()


# =========================================================
# DATABASE
# =========================================================

database.create_tables()


# Add default candidates
if len(database.get_candidates()) == 0:
    database.add_candidate("Candidate A")
    database.add_candidate("Candidate B")
    database.add_candidate("Candidate C")


# =========================================================
# VOTER HOME / LOGIN
# =========================================================

@app.route("/")
def home():

    return render_template("login.html")


# =========================================================
# VOTER REGISTRATION
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        voter_id = request.form["voter_id"]
        name = request.form["name"]
        password = request.form["password"]

        success = database.add_voter(
            voter_id,
            name,
            password
        )

        if success:
            return redirect(url_for("home"))

        return "Voter ID already exists."

    return render_template("register.html")


# =========================================================
# VOTER LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        voter_id = request.form["voter_id"]
        password = request.form["password"]

        voter = database.get_voter(
            voter_id,
            password
        )

        if voter:

            session["voter_id"] = voter_id
            session["name"] = voter[2]

            return redirect(url_for("vote"))

        return "Invalid voter ID or password."

    return render_template("login.html")


# =========================================================
# VOTING
# =========================================================

@app.route("/vote", methods=["GET", "POST"])
def vote():

    if "voter_id" not in session:
        return redirect(url_for("login"))

    voter_id = session["voter_id"]

    voter = database.get_voter_by_id(voter_id)

    # Prevent voting twice
    if voter[4] == 1:
        return "You have already voted."


    if request.method == "POST":

        candidate_id = request.form["candidate"]


        # Cast vote in database
        success = database.cast_vote(
            voter_id,
            candidate_id
        )

        if not success:
            return "You have already voted."


        # Find candidate name
        candidates = database.get_candidates()

        candidate_name = "Unknown"

        for candidate in candidates:

            if str(candidate[0]) == str(candidate_id):

                candidate_name = candidate[1]

                break


        # Add vote to blockchain
        blockchain.add_block(
            f"Voter {voter_id} voted for {candidate_name}"
        )


        return redirect(url_for("results"))


    candidates = database.get_candidates()

    return render_template(
        "vote.html",
        candidates=candidates,
        name=session["name"]
    )


# =========================================================
# RESULTS
# =========================================================

@app.route("/results")
def results():

    candidates = database.get_candidates()

    return render_template(
        "results.html",
        candidates=candidates
    )


# =========================================================
# BLOCKCHAIN VIEW
# =========================================================

@app.route("/blockchain")
def view_blockchain():

    return render_template(
        "blockchain.html",
        blockchain=blockchain.chain,
        valid=blockchain.is_chain_valid()
    )


# =========================================================
# VOTER LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]


        # Demo admin credentials
        if username == "admin" and password == "admin123":

            session["admin"] = True

            return redirect(url_for("admin"))


        return "Invalid admin username or password."


    return render_template("admin_login.html")


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin():

    # Protect admin dashboard
    if not session.get("admin"):

        return redirect(
            url_for("admin_login")
        )


    candidates = database.get_candidates()


    # Calculate total votes
    total_votes = sum(
        candidate[2]
        for candidate in candidates
    )


    return render_template(
        "admin.html",
        candidates=candidates,
        total_votes=total_votes,
        blocks=len(blockchain.chain),
        valid=blockchain.is_chain_valid()
    )

# =========================================================
# RESET VOTES
# =========================================================

@app.route("/admin/reset", methods=["POST"])
def reset_votes():

    global blockchain

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    # Reset votes in the database
    database.reset_votes()

    # Reset blockchain
    blockchain = Blockchain()

    return redirect(url_for("admin"))

# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin", None)

    return redirect(
        url_for("admin_login")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)


