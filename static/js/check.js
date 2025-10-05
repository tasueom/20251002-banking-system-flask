function checkUser(f) {
    const uid = f.uid.value;
    const pw = f.password.value;
    const pwCheck = f.passwordCheck.value;
    const phone = f.phone.value;
    const email = f.email.value;

    const uidPattern = /^[A-Za-z0-9]+$/;
    const phonePattern = /^\d{3}-\d{4}-\d{4}$/;
    const emailPattern = /^[\w.-]+@[\w.-]+\.[A-Za-z]{2,}$/;

    if (!uidPattern.test(uid)) {
        alert("아이디는 영어와 숫자만 입력 가능합니다.");
        f.uid.focus();
        return false;
    }

    if (pw !== pwCheck) {
        alert("비밀번호가 일치하지 않습니다.");
        f.password.focus();
        return false;
    }

    if (!phonePattern.test(phone)) {
        alert("전화번호 형식이 올바르지 않습니다. (예: 010-1234-5678)");
        f.phone.focus();
        return false;
    }

    if (!emailPattern.test(email)) {
        alert("이메일 형식이 올바르지 않습니다.");
        f.email.focus();
        return false;
    }

    return true;
}

function checkAcc(f) {
    const accNo = f.acc_no.value;
    const balance = Number(f.balance.value);

    if (balance < 10000) {
        alert("초기 금액은 최소 10,000원 이상이어야 합니다.");
        f.balance.focus();
        return false;
    }

    return true;
}
