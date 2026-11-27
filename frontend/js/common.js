const API_BASE = "http://127.0.0.1:5000/api";

function getCurrentUser() {
    try {
        const raw = localStorage.getItem("currentUser");
        return raw ? JSON.parse(raw) : null;
    } catch {
        return null;
    }
}

function logout() {
    localStorage.removeItem("currentUser");
    alert("已登出系統");
    window.location.href = "index.html";
}

function requireLogin() {
    const user = getCurrentUser();
    if (!user) {
        alert("請先登入後再使用此功能");
        window.location.href = "index.html";
        return null;
    }
    return user;
}

function renderNavbar(activePage = "") {
    const user = getCurrentUser();
    const navContainer = document.getElementById("navbar");
    if (!navContainer) return;

    const isAdmin = user && user.role_name === "Admin";

    navContainer.innerHTML = `
        <nav style="display:flex; justify-content:space-between; align-items:center; padding:14px 28px; background:#17314b; color:#fff; margin-bottom:24px;">
            <div style="display:flex; align-items:center; gap:20px;">
                <strong style="font-size:18px; letter-spacing:1px;">管院小幫手</strong>
                <a href="spaces.html" style="color:${activePage === 'spaces' ? '#7fe3e8' : '#e2e8f0'}; text-decoration:none;">管院空間查詢</a>
                <a href="bookings.html" style="color:${activePage === 'bookings' ? '#7fe3e8' : '#e2e8f0'}; text-decoration:none;">空間與物品借用</a>
                <a href="courses.html" style="color:${activePage === 'courses' ? '#7fe3e8' : '#e2e8f0'}; text-decoration:none;">課程排課系統</a>
                ${isAdmin ? `<a href="admin_users.html" style="color:${activePage === 'admin_users' ? '#7fe3e8' : '#ffd166'}; text-decoration:none;">帳號與權限管理</a>` : ""}
            </div>
            <div style="display:flex; align-items:center; gap:12px; font-size:14px;">
                ${
                    user
                        ? `<span>您好，<strong>${user.username}</strong>（${user.role_name}）</span>
                           <button onclick="logout()" style="padding:6px 12px; border:none; border-radius:6px; background:#267e83; color:#fff; cursor:pointer;">登出</button>`
                        : `<a href="index.html" style="padding:6px 14px; border-radius:6px; background:#267e83; color:#fff; text-decoration:none;">登入 / 註冊</a>`
                }
            </div>
        </nav>
    `;
}