import PAM

def verify_user(username: str, password: str) -> bool:
    # 1. Define the conversation function PAM will call for the password
    def pam_conv(auth, query_list, userData):
        resp = []
        for query, kind in query_list:
            # 1 = PAM_PROMPT_ECHO_OFF (usually the password prompt)
            if kind == 1:
                resp.append((password, 0))
            else:
                resp.append(("", 0))
        return resp

    # 2. Initialize and configure the PAM object
    auth = PAM.pam()
    auth.start("login")  # Service name from /etc/pam.d/
    auth.set_item(PAM.PAM_USER, username)
    auth.set_item(PAM.PAM_CONV, pam_conv)

    try:
        # 3. Call authenticate with the integer flag 0 (PAM_SILENT)
        # This triggers the pam_conv function defined above
        auth.authenticate(0)
        # Also check account management (e.g., password expired, account locked)
        auth.acct_mgmt(0)
        return True
    except PAM.error as e:
        print(f"Authentication failed: {e}")
        return False
        is_autheticated