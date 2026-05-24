import os
import streamlit as st


class LoginManager:
    @staticmethod
    def is_authenticated() -> bool:
        return st.session_state.get("authenticated", False)

    @staticmethod
    def login(username: str, password: str) -> bool:
        valid_user = os.getenv("APP_USERNAME", "admin")
        valid_pass = os.getenv("APP_PASSWORD", "admin123")
        return username == valid_user and password == valid_pass

    @staticmethod
    def logout() -> None:
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.rerun()

    @staticmethod
    def render_login_page() -> None:
        st.markdown(
            """
            <style>
            .stApp { background-color: #f0fdf4; }
            .login-card {
                max-width: 420px;
                margin: 6vh auto 0 auto;
                background: #ffffff;
                border-radius: 16px;
                padding: 2.5rem 2.5rem 2rem 2.5rem;
                box-shadow: 0 4px 24px rgba(22,163,74,0.10);
                border: 1px solid #bbf7d0;
            }
            .login-logo {
                text-align: center;
                font-size: 2.8rem;
                margin-bottom: 0.3rem;
            }
            .login-title {
                text-align: center;
                color: #15803d;
                font-size: 1.6rem;
                font-weight: 700;
                margin-bottom: 0.2rem;
                letter-spacing: 0.5px;
            }
            .login-subtitle {
                text-align: center;
                color: #64748b;
                font-size: 0.85rem;
                margin-bottom: 1.8rem;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            st.markdown('<div class="login-logo">🌿</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-title">AgenticSQL</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-subtitle">Yapay Zeka Destekli SQL Arayüzü</div>', unsafe_allow_html=True)

            username = st.text_input("Kullanıcı Adı", placeholder="admin", key="login_username")
            password = st.text_input("Şifre", type="password", placeholder="••••••••", key="login_password")

            st.markdown("<br>", unsafe_allow_html=True)
            login_clicked = st.button("Giriş Yap", use_container_width=True, type="primary")

            if login_clicked:
                if not username or not password:
                    st.warning("Lütfen tüm alanları doldurun.")
                elif LoginManager.login(username, password):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre hatalı.")

            st.markdown('</div>', unsafe_allow_html=True)
