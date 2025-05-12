document.addEventListener("DOMContentLoaded", () => {
    // ==========================================
    // AUTH UI AND WORKFLOW ELEMENTS
    // ==========================================
    const loginBtn = document.getElementById("login-btn");
    const registerBtn = document.getElementById("register-btn");
    const loginOptions = document.getElementById("login-options");
    const registerOptions = document.getElementById("register-options");
    const loginForm = document.getElementById("login-form");
    const loginFormTitle = document.getElementById("login-form-title");
    const adminLoginOption = document.getElementById("admin-login-option");
    const candidateLoginOption = document.getElementById("candidate-login-option");
    const voterLoginOption = document.getElementById("voter-login-option");
    const cancelLogin = document.getElementById("cancel-login");
    const closeLoginOptions = document.getElementById("close-login-options");
    const closeRegisterOptions = document.getElementById("close-register-options");
    const candidateRegisterOption = document.getElementById("candidate-register-option");
    const voterRegisterOption = document.getElementById("voter-register-option");

    // Modal Elements
    const howItWorksBtn = document.getElementById("how-it-works");
    const candidateInfoBtn = document.getElementById("candidate-info");
    const voterInfoBtn = document.getElementById("voter-info");
    const candidateInfoModal = document.getElementById("candidate-info-modal");
    const voterInfoModal = document.getElementById("voter-info-modal");
    const closeModalBtns = document.querySelectorAll(".close-modal");

    // Hero Content Elements
    const heroContent = document.querySelector(".hero-content");
    const originalHeroHTML = heroContent ? heroContent.innerHTML : null; // Store the original content if element exists

    // ==========================================
    // SHARED ANIMATION FUNCTIONS
    // ==========================================
    
    // Add animation to headings
    const pageHeading = document.querySelector('.about h2, .contact h2');
    if (pageHeading) {
        pageHeading.style.opacity = '0';
        pageHeading.style.transform = 'translateY(-20px)';
        pageHeading.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        setTimeout(() => {
            pageHeading.style.opacity = '1';
            pageHeading.style.transform = 'translateY(0)';
        }, 100);
    }
    
    // Add animation to blockquotes
    const blockquote = document.querySelector('blockquote');
    if (blockquote) {
        blockquote.style.opacity = '0';
        blockquote.style.transform = 'translateX(-20px)';
        blockquote.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
        
        setTimeout(() => {
            blockquote.style.opacity = '1';
            blockquote.style.transform = 'translateX(0)';
        }, 300);
    }
    
    // ==========================================
    // ABOUT PAGE SPECIFIC FUNCTIONALITY
    // ==========================================
    const aboutSection = document.querySelector('.about');
    if (aboutSection) {
        // Add fade-in effect for paragraphs
        const paragraphs = aboutSection.querySelectorAll('p');
        paragraphs.forEach((paragraph, index) => {
            paragraph.style.opacity = '0';
            paragraph.style.transform = 'translateY(15px)';
            paragraph.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            
            setTimeout(() => {
                paragraph.style.opacity = '1';
                paragraph.style.transform = 'translateY(0)';
            }, 200 + (index * 150));
        });
    }
    
    // ==========================================
    // CONTACT FORM FUNCTIONALITY
    // ==========================================
    const contactForm = document.querySelector('.contact form');
    if (contactForm) {
        // Add enhanced form field interactions
        const formInputs = contactForm.querySelectorAll('input, textarea');
        
        formInputs.forEach(input => {
            // Add focus styles
            input.addEventListener('focus', () => {
                input.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', () => {
                input.parentElement.classList.remove('focused');
                
                // Add class if field has value
                if (input.value.trim() !== '') {
                    input.classList.add('has-value');
                } else {
                    input.classList.remove('has-value');
                }
            });
        });
        
        // Form validation
        contactForm.addEventListener('submit', (e) => {
            let hasError = false;
            
            // Get all required inputs
            const requiredInputs = contactForm.querySelectorAll('[required]');
            
            // Check each required field
            requiredInputs.forEach(input => {
                if (input.value.trim() === '') {
                    e.preventDefault();
                    input.classList.add('error');
                    
                    // Create error message if doesn't exist
                    if (!input.nextElementSibling || !input.nextElementSibling.classList.contains('error-message')) {
                        const errorMessage = document.createElement('div');
                        errorMessage.className = 'error-message';
                        errorMessage.textContent = 'This field is required';
                        input.insertAdjacentElement('afterend', errorMessage);
                    }
                    
                    hasError = true;
                } else {
                    input.classList.remove('error');
                    
                    // Remove error message if exists
                    if (input.nextElementSibling && input.nextElementSibling.classList.contains('error-message')) {
                        input.nextElementSibling.remove();
                    }
                }
            });
            
            // Email validation for email field
            const emailInput = contactForm.querySelector('input[type="email"]');
            if (emailInput && emailInput.value.trim() !== '') {
                const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailPattern.test(emailInput.value)) {
                    e.preventDefault();
                    emailInput.classList.add('error');
                    
                    // Create error message if doesn't exist
                    if (!emailInput.nextElementSibling || !emailInput.nextElementSibling.classList.contains('error-message')) {
                        const errorMessage = document.createElement('div');
                        errorMessage.className = 'error-message';
                        errorMessage.textContent = 'Please enter a valid email address';
                        emailInput.insertAdjacentElement('afterend', errorMessage);
                    }
                    
                    hasError = true;
                }
            }
            
            // Show loading indicator on submit if no errors
            if (!hasError) {
                const submitButton = contactForm.querySelector('button[type="submit"]');
                const originalText = submitButton.textContent;
                
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner"></span> Sending...';
                
                // The form will naturally submit without need to manually submit
            }
        });
        
        // Auto-hide messages after a delay
        const messages = document.querySelectorAll('.messages li');
        if (messages.length > 0) {
            setTimeout(() => {
                messages.forEach(message => {
                    message.style.opacity = '0';
                    message.style.transition = 'opacity 0.5s ease';
                    
                    setTimeout(() => {
                        message.style.display = 'none';
                    }, 500);
                });
            }, 5000);
        }
    }
    
    // ==========================================
    // WORKFLOW HTML TEMPLATES
    // ==========================================
    const workflowHTML = `
    <div class="workflow-container">
        <div class="workflow-header">
            <h2>How Our Election System Works</h2>
            <p>A secure and transparent process from registration to results</p>
        </div>
        
        <div class="workflow-steps">
            <div class="workflow-line"></div>
            
            <div class="workflow-step">
                <div class="step-icon">
                    <i class="fas fa-user-plus"></i>
                    <div class="step-number">1</div>
                </div>
                <div class="step-title">Register</div>
                <div class="step-desc">Create an account with valid ID verification to ensure security</div>
            </div>
            
            <div class="workflow-step">
                <div class="step-icon">
                    <i class="fas fa-sign-in-alt"></i>
                    <div class="step-number">2</div>
                </div>
                <div class="step-title">Login</div>
                <div class="step-desc">Access your secure dashboard with multi-factor authentication</div>
            </div>
            
            <div class="workflow-step">
                <div class="step-icon">
                    <i class="fas fa-vote-yea"></i>
                    <div class="step-number">3</div>
                </div>
                <div class="step-title">Participate</div>
                <div class="step-desc">Cast your vote or run as a candidate in open elections</div>
            </div>
            
            <div class="workflow-step">
                <div class="step-icon">
                    <i class="fas fa-chart-bar"></i>
                    <div class="step-number">4</div>
                </div>
                <div class="step-title">View Results</div>
                <div class="step-desc">Access real-time, transparent and verifiable election results</div>
            </div>
        </div>
        
        <button id="return-hero-btn" class="return-btn">
            <i class="fas fa-arrow-left"></i> Return to Main View
        </button>
    </div>
    `;
    
    const candidateWorkflowHTML = `
    <div class="workflow-container">
        <div class="workflow-header">
            <h2>How to Participate as a Candidate</h2>
            <p>Follow these steps to run for office in our secure election system</p>
        </div>
        
        <div class="workflow-steps">
            <div class="workflow-line"></div>
            
            <div class="workflow-step">
                <div class="step-icon">
                    <i class="fas fa-file-alt"></i>
                    <div class="step-number">1</div>
                </div>
                <div class="step-title">Register</div>
                <div class="step-desc">Submit required identity documents and eligibility proof</div>
            </div>
            
            <div class="workflow-step">
                <div class="step-icon">
                    <i class="fas fa-user-check"></i>
                    <div class="step-number">2</div>
                </div>
                <div class="step-title">Verification</div>
                <div class="step-desc">Wait for admin approval of your candidacy application</div>
            </div>
            
            <div class="workflow-step">
                <div class="step-icon">
                    <i class="fas fa-key"></i>
                    <div class="step-number">3</div>
                </div>
                <div class="step-title">Access</div>
                <div class="step-desc">Login with credentials and update your password</div>
            </div>
            
            <div class="workflow-step">
                <div class="step-icon">
                    <i class="fas fa-bullhorn"></i>
                    <div class="step-number">4</div>
                </div>
                <div class="step-title">Campaign</div>
                <div class="step-desc">Participate in eligible elections and connect with voters</div>
            </div>
            
            <div class="workflow-step">
                <div class="step-icon">
                    <i class="fas fa-chart-pie"></i>
                    <div class="step-number">5</div>
                </div>
                <div class="step-title">Results</div>
                <div class="step-desc">View real-time election results and analytics</div>
            </div>
        </div>
        
        <button id="return-hero-btn" class="return-btn">
            <i class="fas fa-arrow-left"></i> Return to Main View
        </button>
    </div>
    `;
    
    const voterWorkflowHTML = `
    <div class="workflow-container">
        <div class="workflow-header">
            <h2>How to Vote in Our Election System</h2>
            <p>Follow these simple steps to cast your vote securely and transparently</p>
        </div>
        
        <div class="workflow-steps">
            <div class="workflow-line"></div>
            
            <div class="workflow-step">
                <div class="step-icon">
                    <i class="fas fa-id-card"></i>
                    <div class="step-number">1</div>
                </div>
                <div class="step-title">Register</div>
                <div class="step-desc">Submit valid ID documents for verification</div>
            </div>
            
            <div class="workflow-step">
                <div class="step-icon">
                    <i class="fas fa-user-check"></i>
                    <div class="step-number">2</div>
                </div>
                <div class="step-title">Verification</div>
                <div class="step-desc">Wait for admin approval of your voter registration</div>
            </div>
            
            <div class="workflow-step">
                <div class="step-icon">
                    <i class="fas fa-key"></i>
                    <div class="step-number">3</div>
                </div>
                <div class="step-title">Access</div>
                <div class="step-desc">Login with credentials received via email and update password</div>
            </div>
            
            <div class="workflow-step">
                <div class="step-icon">
                    <i class="fas fa-list-ul"></i>
                    <div class="step-number">4</div>
                </div>
                <div class="step-title">View Candidates</div>
                <div class="step-desc">Browse participating candidates and their information</div>
            </div>
            
            <div class="workflow-step">
                <div class="step-icon">
                    <i class="fas fa-vote-yea"></i>
                    <div class="step-number">5</div>
                </div>
                <div class="step-title">Vote</div>
                <div class="step-desc">Cast your secure vote in eligible elections</div>
            </div>
            
            <div class="workflow-step">
                <div class="step-icon">
                    <i class="fas fa-poll"></i>
                    <div class="step-number">6</div>
                </div>
                <div class="step-title">Results</div>
                <div class="step-desc">View real-time election results once voting closes</div>
            </div>
        </div>
        
        <button id="return-hero-btn" class="return-btn">
            <i class="fas fa-arrow-left"></i> Return to Main View
        </button>
    </div>
    `;

    // ==========================================
    // WORKFLOW VIEW FUNCTIONS
    // ==========================================
    // Function to show workflow view
    function showWorkflowView() {
        if (heroContent) {
            heroContent.innerHTML = workflowHTML;
            
            // Add event listener to the return button
            document.getElementById("return-hero-btn").addEventListener("click", () => {
                restoreOriginalHero();
            });
            
            // Add hover effects to workflow steps
            addWorkflowStepHoverEffects();
        }
    }
    
    // Function to show candidate workflow view
    function showCandidateWorkflowView() {
        if (heroContent) {
            heroContent.innerHTML = candidateWorkflowHTML;
            
            // Add event listener to the return button
            document.getElementById("return-hero-btn").addEventListener("click", () => {
                restoreOriginalHero();
            });
            
            // Add hover effects to workflow steps
            addWorkflowStepHoverEffects();
        }
    }
    
    // Function to show voter workflow view
    function showVoterWorkflowView() {
        if (heroContent) {
            heroContent.innerHTML = voterWorkflowHTML;
            
            // Add event listener to the return button
            document.getElementById("return-hero-btn").addEventListener("click", () => {
                restoreOriginalHero();
            });
            
            // Add hover effects to workflow steps
            addWorkflowStepHoverEffects();
        }
    }
    
    // Function to add hover effects to workflow steps
    function addWorkflowStepHoverEffects() {
        document.querySelectorAll(".step-icon").forEach(icon => {
            icon.addEventListener("mouseover", () => {
                icon.style.transform = "scale(1.1)";
                icon.style.backgroundColor = "#ff9933";
                icon.style.color = "white";
                icon.style.boxShadow = "0 0 15px rgba(255, 153, 51, 0.5)";
            });
            
            icon.addEventListener("mouseout", () => {
                icon.style.transform = "";
                icon.style.backgroundColor = "";
                icon.style.color = "";
                icon.style.boxShadow = "";
            });
        });
    }
    
    // Function to restore original hero content
    function restoreOriginalHero() {
        if (heroContent && originalHeroHTML) {
            heroContent.innerHTML = originalHeroHTML;
            
            // Reattach event listeners for the buttons
            const howItWorksBtn = document.getElementById("how-it-works");
            const candidateInfoBtn = document.getElementById("candidate-info");
            const voterInfoBtn = document.getElementById("voter-info");
            
            if (howItWorksBtn) {
                howItWorksBtn.addEventListener("click", showWorkflowView);
            }
            
            if (candidateInfoBtn) {
                candidateInfoBtn.addEventListener("click", (e) => {
                    e.preventDefault();
                    showCandidateWorkflowView();
                });
            }
            
            if (voterInfoBtn) {
                voterInfoBtn.addEventListener("click", (e) => {
                    e.preventDefault();
                    showVoterWorkflowView();
                });
            }
        }
    }

    // ==========================================
    // AUTH UI EVENT LISTENERS
    // ==========================================
    if (loginBtn) {
        loginBtn.addEventListener("click", () => {
            loginOptions.classList.remove("hidden");
            if (registerOptions) registerOptions.classList.add("hidden");
            if (loginForm) loginForm.classList.add("hidden");
        });
    }

    if (registerBtn) {
        registerBtn.addEventListener("click", () => {
            if (registerOptions) registerOptions.classList.remove("hidden");
            if (loginOptions) loginOptions.classList.add("hidden");
            if (loginForm) loginForm.classList.add("hidden");
        });
    }

    if (closeLoginOptions) {
        closeLoginOptions.addEventListener("click", () => {
            loginOptions.classList.add("hidden");
        });
    }

    if (closeRegisterOptions) {
        closeRegisterOptions.addEventListener("click", () => {
            registerOptions.classList.add("hidden");
        });
    }

    if (adminLoginOption) {
        adminLoginOption.addEventListener("click", () => {
            loginFormTitle.textContent = "Admin Login";
            loginForm.action = "/custom-admin-login/";
            loginOptions.classList.add("hidden");
            loginForm.classList.remove("hidden");
        });
    }

    if (candidateLoginOption) {
        candidateLoginOption.addEventListener("click", () => {
            loginFormTitle.textContent = "Candidate Login";
            loginForm.action = "/candidate-login/";
            loginOptions.classList.add("hidden");
            loginForm.classList.remove("hidden");
        });
    }

    if (voterLoginOption) {
        voterLoginOption.addEventListener("click", () => {
            loginFormTitle.textContent = "Voter Login";
            loginForm.action = "/voter-login/";
            loginOptions.classList.add("hidden");
            loginForm.classList.remove("hidden");
        });
    }

    if (cancelLogin) {
        cancelLogin.addEventListener("click", () => {
            loginForm.classList.add("hidden");
        });
    }

    if (candidateRegisterOption) {
        candidateRegisterOption.addEventListener("click", () => {
            window.location.href = "/candidate-registration/";
        });
    }

    if (voterRegisterOption) {
        voterRegisterOption.addEventListener("click", () => {
            window.location.href = "/voter-registration/";
        });
    }

    // ==========================================
    // WORKFLOW BUTTON EVENT LISTENERS
    // ==========================================
    if (howItWorksBtn) {
        howItWorksBtn.addEventListener("click", showWorkflowView);
    }

    if (candidateInfoBtn) {
        candidateInfoBtn.addEventListener("click", (e) => {
            e.preventDefault();
            showCandidateWorkflowView();
        });
    }

    if (voterInfoBtn) {
        voterInfoBtn.addEventListener("click", (e) => {
            e.preventDefault();
            showVoterWorkflowView();
        });
    }

    // ==========================================
    // MODAL HANDLERS
    // ==========================================
    // Close modal buttons
    closeModalBtns.forEach(btn => {
        btn.addEventListener("click", (e) => {
            // Find the parent modal
            const modal = e.target.closest(".modal");
            if (modal) {
                modal.classList.add("hidden");
            }
        });
    });

    // Close modals when clicking outside of modal content
    document.addEventListener("click", (e) => {
        if (e.target.classList.contains("modal")) {
            e.target.classList.add("hidden");
        }
    });

    // Close auth options when clicking outside
    document.addEventListener("click", (e) => {
        if (loginOptions && !loginOptions.classList.contains("hidden") && 
            !e.target.closest(".auth-options") && 
            !e.target.closest("#login-btn") && 
            !e.target.closest("#register-btn")) {
            loginOptions.classList.add("hidden");
        }

        if (registerOptions && !registerOptions.classList.contains("hidden") && 
            !e.target.closest(".auth-options") && 
            !e.target.closest("#login-btn") && 
            !e.target.closest("#register-btn")) {
            registerOptions.classList.add("hidden");
        }
    });

    // ==========================================
    // LOGIN FORM SUBMISSION
    // ==========================================
    if (loginForm) {
        loginForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const username = loginForm.querySelector('input[name="username"]').value;
            const password = loginForm.querySelector('input[name="password"]').value;
            
            // Validate input
            if (!username || !password) {
                alert("Please enter both username and password.");
                return;
            }
            
            // Submit the form normally
            loginForm.submit();
        });
    }

    // ==========================================
    // NEWS CARD CLICK HANDLERS
    // ==========================================
    const newsCards = document.querySelectorAll(".news-card");
    newsCards.forEach(card => {
        card.addEventListener("click", (e) => {
            if (!e.target.classList.contains("read-more")) {
                const readMoreLink = card.querySelector(".read-more");
                if (readMoreLink) {
                    readMoreLink.click();
                }
            }
        });
    });

    // ==========================================
    // URL PARAMETER HANDLERS
    // ==========================================
    const searchParams = new URLSearchParams(window.location.search);
    // Handle form errors
    if (searchParams.has("error")) {
        const errorType = searchParams.get("error");
        if (errorType === "login") {
            alert("Invalid username or password. Please try again.");
        } else if (errorType === "register") {
            alert("Registration failed. Please try again.");
        }
    }

    // Handle successful actions
    if (searchParams.has("success")) {
        const successType = searchParams.get("success");
        if (successType === "register") {
            alert("Registration successful! You can now log in.");
        }
    }

    // ==========================================
    // KEYBOARD ACCESSIBILITY
    // ==========================================
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            // Close any open modals
            document.querySelectorAll(".modal").forEach(modal => {
                modal.classList.add("hidden");
            });
            
            // Close any open auth options
            if (loginOptions) loginOptions.classList.add("hidden");
            if (registerOptions) registerOptions.classList.add("hidden");
            if (loginForm) loginForm.classList.add("hidden");
        }
    });
});

