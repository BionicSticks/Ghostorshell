import hashlib
import streamlit as st
import json
from typing import Optional

def get_client_ip() -> str:
    """Get client IP address from Streamlit context"""
    try:
        # Try to get real IP from headers
        headers = st.context.headers if hasattr(st.context, 'headers') else {}
        
        # Check common proxy headers
        forwarded_ips = [
            headers.get('X-Forwarded-For', '').split(',')[0].strip(),
            headers.get('X-Real-Ip', ''),
            headers.get('CF-Connecting-IP', ''),  # Cloudflare
            headers.get('X-Client-IP', '')
        ]
        
        for ip in forwarded_ips:
            if ip and ip != 'unknown':
                return ip
                
        # Fallback to session info or default
        return getattr(st.session_state, 'client_ip', '127.0.0.1')
        
    except Exception:
        return '127.0.0.1'

def get_browser_fingerprint() -> str:
    """Create browser fingerprint from available client info"""
    try:
        # Get basic client info that's available in Streamlit
        user_agent = st.context.headers.get('User-Agent', '') if hasattr(st.context, 'headers') else ''
        accept_language = st.context.headers.get('Accept-Language', '') if hasattr(st.context, 'headers') else ''
        
        # Use session state to store additional fingerprint data
        if 'browser_fingerprint_data' not in st.session_state:
            st.session_state.browser_fingerprint_data = {
                'user_agent': user_agent,
                'accept_language': accept_language,
                'timezone_offset': None,  # Could be set via JavaScript component
                'screen_info': None       # Could be set via JavaScript component
            }
        
        fingerprint_data = st.session_state.browser_fingerprint_data
        
        # Create fingerprint string
        fingerprint_string = f"{fingerprint_data['user_agent']}|{fingerprint_data['accept_language']}|{fingerprint_data.get('timezone_offset', '')}|{fingerprint_data.get('screen_info', '')}"
        
        return fingerprint_string
        
    except Exception:
        return "unknown_browser"

def generate_visitor_id(ip_address: str, browser_fingerprint: str) -> str:
    """Generate unique visitor ID from IP and browser fingerprint"""
    try:
        # Combine IP and browser fingerprint
        combined_data = f"{ip_address}|{browser_fingerprint}"
        
        # Create SHA-256 hash
        visitor_hash = hashlib.sha256(combined_data.encode('utf-8')).hexdigest()
        
        # Return first 32 characters for database storage
        return visitor_hash[:32]
        
    except Exception:
        # Fallback to IP-based hash
        ip_hash = hashlib.sha256(ip_address.encode('utf-8')).hexdigest()
        return ip_hash[:32]

def get_visitor_id() -> tuple[str, str]:
    """Get visitor ID and IP address for current session"""
    # Get client information
    ip_address = get_client_ip()
    browser_fingerprint = get_browser_fingerprint()
    
    # Generate visitor ID
    visitor_id = generate_visitor_id(ip_address, browser_fingerprint)
    
    return visitor_id, ip_address

def initialize_visitor_tracking():
    """Initialize visitor tracking for the current session"""
    if 'visitor_id' not in st.session_state:
        visitor_id, ip_address = get_visitor_id()
        st.session_state.visitor_id = visitor_id
        st.session_state.visitor_ip = ip_address
    
    return st.session_state.visitor_id, st.session_state.visitor_ip