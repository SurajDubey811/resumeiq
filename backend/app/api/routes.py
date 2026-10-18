from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.config import settings
from app.models.schemas import (
    HealthResponse,
    ParseResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    ParsedResume,
    ImproveRequest,
    ImproveResponse,
)
from app.parser.extractor import (
    parse_resume_bytes,
    EmptyFileError,
    OversizedFileError,
    InvalidFileType,
    EncryptedPDFError,
    ResumeParsingError,
)
from app.utils.logger import get_logger

logger = get_logger("resumeiq.api")
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint providing status and runtime info."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        app_name=settings.app_name
    )


@router.post("/resumes/parse", response_model=ParseResponse)
async def parse_resume(file: UploadFile = File(...)):
    """
    Parses an uploaded PDF or DOCX resume.
    Processes the file strictly in-memory (ephemeral zero retention).
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing filename."
        )

    logger.info(f"Received parse request for file: {file.filename}")

    try:
        # Read contents with streaming check for size limit
        content = await file.read()
        
        if len(content) > settings.max_upload_size_bytes:
            limit_mb = settings.max_upload_size_bytes // (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Uploaded file exceeds the maximum allowed size of {limit_mb}MB."
            )

        parsed_resume = parse_resume_bytes(content, file.filename)
        return ParseResponse(
            success=True,
            data=parsed_resume
        )

    except EmptyFileError as e:
        logger.warning(f"Empty file uploaded: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except OversizedFileError as e:
        logger.warning(f"Oversized file: {str(e)}")
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(e))
    except InvalidFileType as e:
        logger.warning(f"Invalid file type: {str(e)}")
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(e))
    except EncryptedPDFError as e:
        logger.warning(f"Encrypted PDF: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except ResumeParsingError as e:
        logger.error(f"Resume parsing error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected parsing error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while parsing the document.")
    finally:
        # Guarantee cleanup of uploaded file temporary handle
        await file.close()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resume(request: AnalyzeRequest):
    """
    Analyzes resume against job description (or runs resume-only general ATS check).
    Produces deterministic, explainable scores out of 100 with category breakdowns.
    """
    if not request.resume_text or not request.resume_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text cannot be empty."
        )

    logger.info("Analyzing resume (Job-mode: %s)", bool(request.job_description and request.job_description.strip()))

    try:
        from app.engine.scorer import calculate_ats_score
        from app.parser.section_parser import parse_sections, extract_contact_info

        # Use provided parsed_resume or construct from resume_text
        if request.parsed_resume:
            parsed = request.parsed_resume
        else:
            sections = parse_sections(request.resume_text)
            contact_info = extract_contact_info(request.resume_text)
            parsed = ParsedResume(
                filename=request.filename or "resume.pdf",
                file_type="pdf" if (request.filename or "").lower().endswith(".pdf") else "docx",
                word_count=len(request.resume_text.split()),
                page_count=max(1, len(request.resume_text.split()) // 450),
                raw_text=request.resume_text,
                contact_info=contact_info,
                sections=sections,
                is_scanned_pdf=False,
                ocr_recommended=False,
                warnings=[]
            )

        scorecard = calculate_ats_score(parsed, request.job_description)
        return AnalyzeResponse(
            success=True,
            scorecard=scorecard
        )
    except Exception as e:
        logger.error(f"Analysis engine error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during ATS analysis: {str(e)}"
        )


@router.post("/resumes/improve", response_model=ImproveResponse)
async def improve_resume(request: ImproveRequest):
    """
    Generates side-by-side revision suggestions for selected resume bullet points.
    Defaults to Layer A (Local Rule-based).
    If use_ai is True and API key is present, utilizes Layer B (AI Provider).
    """
    if not request.resume_text or not request.resume_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text cannot be empty."
        )

    try:
        from app.ai.mock_provider import LocalRuleBasedRewriter
        from app.ai.gemini_provider import GeminiAIProvider

        ai_used = False
        disclaimer = "Generated using local rule-based engine (Layer A). Operates with zero network data transmission and strict factual alignment."

        if request.use_ai:
            provider = GeminiAIProvider()
            if provider.api_key:
                ai_used = True
                disclaimer = "Generated using AI assistance (Layer B). Suggestions are heuristic estimates and have been validated against our factual accuracy constraints."
            else:
                provider = LocalRuleBasedRewriter()
        else:
            provider = LocalRuleBasedRewriter()

        suggestions = await provider.suggest_improvements(
            resume_text=request.resume_text,
            job_description=request.job_description,
            sections=request.sections,
            focus_areas=request.focus_areas
        )

        return ImproveResponse(
            success=True,
            suggestions=suggestions,
            ai_used=ai_used,
            disclaimer=disclaimer
        )

    except Exception as e:
        logger.error(f"Improvement error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate resume improvements: {str(e)}"
        )

