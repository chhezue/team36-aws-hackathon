// LocalBriefing Mobile App JavaScript

let currentStep = 1;

// Smooth step transitions with mobile-like animations
function nextStep() {
    if (currentStep === 2) {
        const guSelect = document.getElementById('gu-select');
        if (!guSelect.value) {
            showNotification('거주하시는 구를 선택해주세요.', 'warning');
            return;
        }
    }

    const currentStepEl = document.getElementById(`step${currentStep}`);
    const nextStepEl = document.getElementById(`step${currentStep + 1}`);
    
    if (currentStepEl && nextStepEl) {
        // iOS-like slide transition
        currentStepEl.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        currentStepEl.style.opacity = '0';
        currentStepEl.style.transform = 'translateX(-100%)';
        
        setTimeout(() => {
            currentStepEl.style.display = 'none';
            currentStep++;
            
            // Slide in next step
            nextStepEl.style.display = 'block';
            nextStepEl.style.opacity = '0';
            nextStepEl.style.transform = 'translateX(100%)';
            nextStepEl.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            
            setTimeout(() => {
                nextStepEl.style.opacity = '1';
                nextStepEl.style.transform = 'translateX(0)';
            }, 50);
        }, 300);
    }
}

function selectAll() {
    const items = document.querySelectorAll('.category-item');
    items.forEach((item, index) => {
        setTimeout(() => {
            item.classList.add('selected');
            // iOS-like bounce animation
            item.style.transform = 'scale(1.05)';
            setTimeout(() => {
                item.style.transform = 'scale(1)';
            }, 150);
        }, index * 100);
    });
    showNotification('모든 카테고리가 선택되었습니다!', 'success');
}

function toggleSwitch(element) {
    element.classList.toggle('active');
    
    // Haptic feedback simulation
    if (navigator.vibrate) {
        navigator.vibrate([10]);
    }
    
    // iOS-like animation
    element.style.transform = 'scale(0.95)';
    setTimeout(() => {
        element.style.transform = 'scale(1)';
    }, 100);
}

// Enhanced notification system with iOS-style design
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.app-notification');
    existingNotifications.forEach(notif => notif.remove());
    
    const notification = document.createElement('div');
    notification.className = `app-notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">${getNotificationIcon(type)}</span>
            <span class="notification-text">${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // iOS-style slide down animation
    setTimeout(() => {
        notification.classList.add('show');
        // Initialize icons in notification
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }, 100);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function getNotificationIcon(type) {
    const icons = {
        success: '<i data-lucide="check-circle" style="width: 18px; height: 18px; color: var(--success);"></i>',
        warning: '<i data-lucide="alert-triangle" style="width: 18px; height: 18px; color: var(--warning);"></i>',
        error: '<i data-lucide="x-circle" style="width: 18px; height: 18px; color: var(--error);"></i>',
        info: '<i data-lucide="info" style="width: 18px; height: 18px; color: var(--primary);"></i>'
    };
    return icons[type] || icons.info;
}

// Enhanced card interactions with iOS-style feedback
function addCardInteractions() {
    const cards = document.querySelectorAll('.app-card, .category-item, .app-button');
    
    cards.forEach(card => {
        // Touch start
        card.addEventListener('touchstart', function(e) {
            this.style.transform = 'scale(0.98)';
            this.style.transition = 'transform 0.1s ease';
        }, { passive: true });
        
        // Touch end
        card.addEventListener('touchend', function(e) {
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 100);
        }, { passive: true });
        
        // Mouse events for desktop
        card.addEventListener('mousedown', function(e) {
            this.style.transform = 'scale(0.98)';
            this.style.transition = 'transform 0.1s ease';
        });
        
        card.addEventListener('mouseup', function(e) {
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 100);
        });
        
        card.addEventListener('mouseleave', function(e) {
            this.style.transform = 'scale(1)';
        });
    });
}

// Enhanced category selection with iOS-style animations
function enhanceCategorySelection() {
    const categoryItems = document.querySelectorAll('.category-item');
    
    categoryItems.forEach(item => {
        item.addEventListener('click', function(e) {
            this.classList.toggle('selected');
            
            // iOS-style selection animation
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
            
            // Haptic feedback
            if (navigator.vibrate) {
                navigator.vibrate([10]);
            }
        });
    });
}

// iOS-style pull to refresh (visual only)
function initPullToRefresh() {
    let startY = 0;
    let currentY = 0;
    let pullDistance = 0;
    const threshold = 100;
    
    const container = document.querySelector('.container');
    if (!container) return;
    
    container.addEventListener('touchstart', function(e) {
        startY = e.touches[0].clientY;
    }, { passive: true });
    
    container.addEventListener('touchmove', function(e) {
        if (window.scrollY > 0) return;
        
        currentY = e.touches[0].clientY;
        pullDistance = currentY - startY;
        
        if (pullDistance > 0 && pullDistance < threshold) {
            const opacity = pullDistance / threshold;
            container.style.transform = `translateY(${pullDistance * 0.5}px)`;
            
            // Show pull indicator
            if (!document.querySelector('.pull-indicator')) {
                const indicator = document.createElement('div');
                indicator.className = 'pull-indicator';
                indicator.innerHTML = '↓ 당겨서 새로고침';
                indicator.style.opacity = opacity;
                container.prepend(indicator);
            } else {
                document.querySelector('.pull-indicator').style.opacity = opacity;
            }
        }
    }, { passive: true });
    
    container.addEventListener('touchend', function(e) {
        if (pullDistance > threshold) {
            // Trigger refresh
            showNotification('새로고침 중...', 'info');
            setTimeout(() => {
                location.reload();
            }, 1000);
        }
        
        // Reset
        container.style.transform = 'translateY(0)';
        const indicator = document.querySelector('.pull-indicator');
        if (indicator) {
            indicator.remove();
        }
        pullDistance = 0;
    }, { passive: true });
}

// Initialize all enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Original functionality
    const guSelect = document.getElementById('gu-select');
    
    if (guSelect) {
        guSelect.addEventListener('change', function() {
            const selectedDistrict = this.value;
            if (selectedDistrict) {
                localStorage.setItem('selectedDistrict', selectedDistrict);
                showNotification(`${selectedDistrict}가 선택되었습니다.`, 'success');
            }
        });
    }
    
    const savedDistrict = localStorage.getItem('selectedDistrict');
    if (savedDistrict && guSelect) {
        guSelect.value = savedDistrict;
    }
    
    // Enhanced mobile features
    addCardInteractions();
    enhanceCategorySelection();
    initPullToRefresh();
    
    // Add mobile-specific CSS
    const style = document.createElement('style');
    style.textContent = `
        /* Mobile App Notifications */
        .app-notification {
            position: fixed;
            top: -100px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--bg-card);
            border: 1px solid var(--text-tertiary);
            border-radius: var(--radius-large);
            padding: var(--spacing-md) var(--spacing-lg);
            box-shadow: var(--shadow-heavy);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 1000;
            max-width: 320px;
            width: 90%;
        }
        
        .app-notification.show {
            top: 60px;
        }
        
        .notification-content {
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
        }
        
        .notification-text {
            color: var(--text-primary);
            font-size: 15px;
            font-weight: 500;
        }
        
        .notification-icon {
            font-size: 18px;
        }
        
        .app-notification.success {
            border-color: var(--success);
        }
        
        .app-notification.warning {
            border-color: var(--warning);
        }
        
        .app-notification.error {
            border-color: var(--error);
        }
        
        /* Pull to Refresh Indicator */
        .pull-indicator {
            text-align: center;
            padding: var(--spacing-md);
            color: var(--text-secondary);
            font-size: 14px;
            font-weight: 500;
            transition: opacity 0.2s ease;
        }
        
        /* Enhanced Touch Interactions */
        .app-card, .category-item, .app-button {
            -webkit-tap-highlight-color: transparent;
            user-select: none;
        }
        
        /* iOS-style Selection */
        .category-item.selected {
            background: var(--primary) !important;
            color: var(--text-white) !important;
        }
        
        .category-item.selected .category-title,
        .category-item.selected .category-desc {
            color: var(--text-white) !important;
        }
        
        /* Smooth Transitions */
        .onboarding-step {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* Loading States */
        .loading {
            opacity: 0.6;
            pointer-events: none;
        }
        
        /* Safe Area Support for iPhone */
        @supports (padding: max(0px)) {
            .container {
                padding-top: max(var(--spacing-lg), env(safe-area-inset-top));
                padding-bottom: max(var(--spacing-lg), env(safe-area-inset-bottom));
                padding-left: max(var(--spacing-md), env(safe-area-inset-left));
                padding-right: max(var(--spacing-md), env(safe-area-inset-right));
            }
        }
    `;
    document.head.appendChild(style);
    
    // Add viewport meta tag if not present
    if (!document.querySelector('meta[name="viewport"]')) {
        const viewport = document.createElement('meta');
        viewport.name = 'viewport';
        viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover';
        document.head.appendChild(viewport);
    }
});

// Service Worker registration for PWA-like experience
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js').then(function(registration) {
            console.log('SW registered: ', registration);
        }).catch(function(registrationError) {
            console.log('SW registration failed: ', registrationError);
        });
    });
}