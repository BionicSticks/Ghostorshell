import streamlit as st
import os
from ai_detector import AIDetector
from file_processor import FileProcessor
from database import DatabaseManager
import time

# Configure page
st.set_page_config(
    page_title="GhostOrShell - AI Content Detection",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize processors
@st.cache_resource
def init_processors():
    return AIDetector(), FileProcessor(), DatabaseManager()

def main():
    # Custom CSS for sleek styling
    st.markdown("""
    <style>
    .main-header {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-weight: 600;
        font-size: 2.5rem;
        color: #0f172a;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-weight: 400;
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 0.5rem 0;
    }
    .result-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 0.75rem;
        padding: 2rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.375rem;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.25rem 0;
    }
    .status-ai {
        background-color: #fef2f2;
        color: #dc2626;
        border: 1px solid #fecaca;
    }
    .status-human {
        background-color: #f0fdf4;
        color: #059669;
        border: 1px solid #bbf7d0;
    }
    .status-uncertain {
        background-color: #fffbeb;
        color: #d97706;
        border: 1px solid #fed7aa;
    }
    .upload-area {
        border: 2px dashed #cbd5e1;
        border-radius: 0.5rem;
        padding: 2rem;
        text-align: center;
        background: #f8fafc;
        transition: all 0.2s ease;
    }
    .upload-area:hover {
        border-color: #3b82f6;
        background: #f0f9ff;
    }
    .stTab {
        font-family: 'Inter', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">GhostOrShell</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Advanced AI content detection and analysis platform</p>', unsafe_allow_html=True)
    
    # Create tabs with cleaner styling
    tab1, tab2 = st.tabs(["Analyze Document", "Analysis History"])
    
    with tab1:
        analyze_document_tab()
    
    with tab2:
        analysis_history_tab()

def analyze_document_tab():
    # Main content area
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### Upload Document")
        
        # API Key status check
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("OpenAI API key required. Please configure your API key to continue.")
            st.stop()
        
        # File upload section
        st.markdown("""
        <div class="upload-area">
            <p style="margin: 0; color: #64748b;">Drag and drop your file here or click to browse</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.875rem; color: #94a3b8;">Supported: .txt, .pdf, .docx (max 10MB)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # File uploader
        uploaded_file = st.file_uploader(
            "",
            type=["txt", "pdf", "docx"],
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            # Display file info in clean format
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="margin: 0 0 0.5rem 0; color: #0f172a;">File Details</h4>
                <p style="margin: 0.25rem 0; color: #64748b;"><strong>Name:</strong> {uploaded_file.name}</p>
                <p style="margin: 0.25rem 0; color: #64748b;"><strong>Size:</strong> {uploaded_file.size / 1024:.1f} KB</p>
                <p style="margin: 0.25rem 0; color: #64748b;"><strong>Type:</strong> {uploaded_file.type}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Process button
            if st.button("Analyze Content", type="primary", use_container_width=True):
                try:
                    # Initialize processors
                    ai_detector, file_processor, db_manager = init_processors()
                    
                    # Show processing status
                    with st.spinner("Processing file..."):
                        # Extract text based on file type
                        text_content = file_processor.extract_text(uploaded_file)
                        
                        if not text_content or len(text_content.strip()) < 10:
                            st.error("Could not extract sufficient text from the file")
                            return
                        
                        # Store results in session state
                        st.session_state.extracted_text = text_content
                        st.session_state.file_name = uploaded_file.name
                    
                    with st.spinner("Analyzing content..."):
                        # Analyze for AI content
                        detection_result = ai_detector.detect_ai_content(text_content)
                        st.session_state.detection_result = detection_result
                    
                    # Save to database
                    with st.spinner("Saving results..."):
                        try:
                            file_extension = uploaded_file.name.split('.')[-1].lower()
                            record_id = db_manager.save_analysis(
                                filename=uploaded_file.name,
                                file_type=file_extension,
                                file_size=uploaded_file.size,
                                text_length=len(text_content),
                                ai_probability=detection_result['ai_probability'],
                                confidence=detection_result['confidence'],
                                reasoning=detection_result['reasoning']
                            )
                            st.session_state.record_id = record_id
                        except Exception as db_error:
                            st.warning(f"Analysis complete but database save failed: {db_error}")
                    
                    st.success("Analysis complete and saved")
                    
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
    
    with col2:
        st.markdown("### Analysis Results")
        
        # Display results if available
        if hasattr(st.session_state, 'detection_result') and st.session_state.detection_result:
            result = st.session_state.detection_result
            
            # AI Probability Score
            ai_probability = result.get('ai_probability', 0)
            confidence = result.get('confidence', 0)
            
            # Determine result classification
            if ai_probability >= 0.7:
                badge_class = "status-ai"
                result_text = "AI Generated"
            elif ai_probability >= 0.3:
                badge_class = "status-uncertain"
                result_text = "Uncertain"
            else:
                badge_class = "status-human"
                result_text = "Human Written"
            
            # Display main result in clean card
            st.markdown(f"""
            <div class="result-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                    <h3 style="margin: 0; color: #0f172a;">Detection Result</h3>
                    <span class="status-badge {badge_class}">{result_text}</span>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
                    <div>
                        <p style="margin: 0; font-size: 0.875rem; color: #64748b;">AI Probability</p>
                        <p style="margin: 0; font-size: 1.5rem; font-weight: 600; color: #0f172a;">{ai_probability:.1%}</p>
                    </div>
                    <div>
                        <p style="margin: 0; font-size: 0.875rem; color: #64748b;">Confidence</p>
                        <p style="margin: 0; font-size: 1.5rem; font-weight: 600; color: #0f172a;">{confidence:.1%}</p>
                    </div>
                </div>
                
                <div style="margin-bottom: 1rem;">
                    <div style="background: #f1f5f9; border-radius: 0.375rem; height: 0.5rem; overflow: hidden;">
                        <div style="background: #3b82f6; height: 100%; width: {ai_probability * 100}%; transition: width 0.3s ease;"></div>
                    </div>
                    <p style="margin: 0.25rem 0 0 0; font-size: 0.75rem; color: #64748b;">AI Likelihood</p>
                </div>
                
                <div>
                    <div style="background: #f1f5f9; border-radius: 0.375rem; height: 0.5rem; overflow: hidden;">
                        <div style="background: #10b981; height: 100%; width: {confidence * 100}%; transition: width 0.3s ease;"></div>
                    </div>
                    <p style="margin: 0.25rem 0 0 0; font-size: 0.75rem; color: #64748b;">Confidence Score</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Analysis reasoning
            if result.get('reasoning'):
                st.markdown("### Analysis Details")
                st.markdown(f"""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 1rem; margin: 1rem 0;">
                    <p style="margin: 0; color: #374151; line-height: 1.6;">{result['reasoning']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Show extracted text preview
            if st.session_state.get('extracted_text'):
                with st.expander("View extracted text"):
                    text_preview = st.session_state.extracted_text[:1000]
                    if len(st.session_state.extracted_text) > 1000:
                        text_preview += "..."
                    st.text_area("", text_preview, height=200, disabled=True, label_visibility="collapsed")
        
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem 1rem; color: #64748b;">
                <h4 style="margin: 0 0 0.5rem 0; color: #94a3b8;">No Analysis Yet</h4>
                <p style="margin: 0;">Upload a document on the left to get started</p>
            </div>
            """, unsafe_allow_html=True)

def analysis_history_tab():
    """Display analysis history and statistics"""
    try:
        ai_detector, file_processor, db_manager = init_processors()
        
        st.markdown("### Statistics Overview")
        
        # Get statistics
        try:
            stats = db_manager.get_analysis_stats()
            
            # Display key metrics in clean cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <p style="margin: 0; font-size: 0.875rem; color: #64748b;">Total Analyses</p>
                    <p style="margin: 0; font-size: 2rem; font-weight: 600; color: #0f172a;">{stats['total_analyses']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <p style="margin: 0; font-size: 0.875rem; color: #64748b;">AI Detected</p>
                    <p style="margin: 0; font-size: 2rem; font-weight: 600; color: #dc2626;">{stats['ai_detected']}</p>
                    <p style="margin: 0; font-size: 0.75rem; color: #94a3b8;">{stats['ai_percentage']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <p style="margin: 0; font-size: 0.875rem; color: #64748b;">Human Detected</p>
                    <p style="margin: 0; font-size: 2rem; font-weight: 600; color: #059669;">{stats['human_detected']}</p>
                    <p style="margin: 0; font-size: 0.75rem; color: #94a3b8;">{stats['human_percentage']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <p style="margin: 0; font-size: 0.875rem; color: #64748b;">Avg Confidence</p>
                    <p style="margin: 0; font-size: 2rem; font-weight: 600; color: #0f172a;">{stats['average_confidence']:.0%}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # File type distribution
            if stats['file_type_distribution']:
                st.markdown("### File Type Distribution")
                
                col_chart, col_list = st.columns([2, 1])
                
                with col_chart:
                    file_types = list(stats['file_type_distribution'].keys())
                    file_counts = list(stats['file_type_distribution'].values())
                    st.bar_chart(dict(zip(file_types, file_counts)))
                
                with col_list:
                    for ft, count in stats['file_type_distribution'].items():
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #f1f5f9;">
                            <span style="color: #374151;">{ft}</span>
                            <span style="color: #6b7280; font-weight: 500;">{count}</span>
                        </div>
                        """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error loading statistics: {e}")
        
        # Recent analyses
        st.markdown("### Recent Analyses")
        
        try:
            recent_analyses = db_manager.get_recent_analyses(limit=15)
            
            if recent_analyses:
                for record in recent_analyses:
                    ai_prob = record.ai_probability
                    
                    # Determine status
                    if ai_prob >= 0.7:
                        badge_class = "status-ai"
                        result_text = "AI Generated"
                    elif ai_prob >= 0.3:
                        badge_class = "status-uncertain"
                        result_text = "Uncertain"
                    else:
                        badge_class = "status-human"
                        result_text = "Human Written"
                    
                    with st.expander(f"{record.filename} - {record.created_at.strftime('%m/%d %H:%M')}"):
                        st.markdown(f"""
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 1rem;">
                            <div>
                                <h4 style="margin: 0 0 0.5rem 0; color: #0f172a;">File Details</h4>
                                <p style="margin: 0.25rem 0; color: #64748b;"><strong>Name:</strong> {record.filename}</p>
                                <p style="margin: 0.25rem 0; color: #64748b;"><strong>Type:</strong> {record.file_type}</p>
                                <p style="margin: 0.25rem 0; color: #64748b;"><strong>Size:</strong> {record.file_size / 1024:.1f} KB</p>
                                <p style="margin: 0.25rem 0; color: #64748b;"><strong>Characters:</strong> {record.text_length:,}</p>
                                <p style="margin: 0.25rem 0; color: #64748b;"><strong>Date:</strong> {record.created_at.strftime('%Y-%m-%d %H:%M')}</p>
                            </div>
                            <div>
                                <h4 style="margin: 0 0 0.5rem 0; color: #0f172a;">Analysis Result</h4>
                                <div style="margin-bottom: 1rem;">
                                    <span class="status-badge {badge_class}">{result_text}</span>
                                </div>
                                <p style="margin: 0.25rem 0; color: #64748b;"><strong>AI Probability:</strong> {ai_prob:.1%}</p>
                                <p style="margin: 0.25rem 0; color: #64748b;"><strong>Confidence:</strong> {record.confidence:.1%}</p>
                                
                                <div style="margin-top: 1rem;">
                                    <div style="background: #f1f5f9; border-radius: 0.25rem; height: 0.25rem; overflow: hidden;">
                                        <div style="background: #3b82f6; height: 100%; width: {ai_prob * 100}%;"></div>
                                    </div>
                                    <p style="margin: 0.25rem 0 0 0; font-size: 0.75rem; color: #9ca3af;">AI Likelihood</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if record.reasoning:
                            st.markdown("**Analysis Reasoning:**")
                            st.markdown(f"""
                            <div style="background: #f8fafc; border-left: 3px solid #3b82f6; padding: 1rem; margin: 0.5rem 0; border-radius: 0 0.25rem 0.25rem 0;">
                                <p style="margin: 0; color: #374151; line-height: 1.5;">{record.reasoning}</p>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center; padding: 3rem 1rem; color: #64748b;">
                    <h4 style="margin: 0 0 0.5rem 0; color: #94a3b8;">No Analysis History</h4>
                    <p style="margin: 0;">Analyze some documents to see results here</p>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error loading recent analyses: {e}")
            
        # Database management
        st.markdown("### Database Management")
        
        col_clean, col_refresh = st.columns(2)
        
        with col_clean:
            if st.button("Clean Old Records", help="Remove records older than 30 days"):
                try:
                    deleted = db_manager.delete_old_records(days_old=30)
                    st.success(f"Removed {deleted} old records")
                except Exception as e:
                    st.error(f"Error cleaning records: {e}")
        
        with col_refresh:
            if st.button("Refresh Data", help="Reload statistics and history"):
                st.rerun()
                
    except Exception as e:
        st.error(f"Database connection error: {e}")
        st.info("Ensure the database is properly configured.")

if __name__ == "__main__":
    main()
