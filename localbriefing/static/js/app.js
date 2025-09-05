// LocalBriefing 2025 Enhanced JavaScript

let currentStep = 1;

// Smooth step transitions with animations
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
    // Fade out current step
    currentStepEl.style.opacity = '0';
    currentStepEl.style.transform = 'translateY(-20px)';
    
    setTimeout(() => {
      currentStepEl.style.display = 'none';
      currentStep++;
      
      // Fade in next step
      nextStepEl.style.display = 'block';
      nextStepEl.style.opacity = '0';
      nextStepEl.style.transform = 'translateY(20px)';
      
      setTimeout(() => {
        nextStepEl.style.opacity = '1';
        nextStepEl.style.transform = 'translateY(0)';
      }, 50);
    }, 300);
  }
}

function selectAll() {
  const items = document.querySelectorAll('.category-item');
  items.forEach((item, index) => {
    setTimeout(() => {
      item.classList.add('selected');
      item.style.transform = 'scale(1.05)';
      setTimeout(() => {
        item.style.transform = 'scale(1)';
      }, 200);
    }, index * 100);
  });
  showNotification('모든 카테고리가 선택되었습니다!', 'success');
}

function toggleSwitch(element) {
  element.classList.toggle('active');
  
  // Add haptic feedback simulation
  if (navigator.vibrate) {
    navigator.vibrate(50);
  }
}

// Enhanced notification system
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.innerHTML = `
    <div class="notification-content">
      <span class="notification-icon">${getNotificationIcon(type)}</span>
      <span class="notification-text">${message}</span>
    </div>
  `;
  
  document.body.appendChild(notification);
  
  // Animate in
  setTimeout(() => {
    notification.classList.add('show');
  }, 100);
  
  // Remove after 3 seconds
  setTimeout(() => {
    notification.classList.remove('show');
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 300);
  }, 3000);
}

function getNotificationIcon(type) {
  const icons = {
    success: '✅',
    warning: '⚠️',
    error: '❌',
    info: 'ℹ️'
  };
  return icons[type] || icons.info;
}

// Enhanced card interactions
function addCardHoverEffects() {
  const cards = document.querySelectorAll('.glass-card, .category-item');
  
  cards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-4px) scale(1.02)';
    });
    
    card.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0) scale(1)';
    });
  });
}

// Parallax effect for background
function initParallax() {
  let ticking = false;
  
  function updateParallax() {
    const scrolled = window.pageYOffset;
    const parallax = document.querySelector('body');
    const speed = scrolled * 0.5;
    
    if (parallax) {
      parallax.style.backgroundPosition = `center ${speed}px`;
    }
    
    ticking = false;
  }
  
  function requestTick() {
    if (!ticking) {
      requestAnimationFrame(updateParallax);
      ticking = true;
    }
  }
  
  window.addEventListener('scroll', requestTick);
}

// Enhanced category selection with animations
function enhanceCategorySelection() {
  const categoryItems = document.querySelectorAll('.category-item');
  
  categoryItems.forEach(item => {
    item.addEventListener('click', function() {
      this.classList.toggle('selected');
      
      // Add selection animation
      this.style.transform = 'scale(0.95)';
      setTimeout(() => {
        this.style.transform = 'scale(1)';
      }, 150);
      
      // Add particle effect
      createParticleEffect(this);
    });
  });
}

// Particle effect for interactions
function createParticleEffect(element) {
  const rect = element.getBoundingClientRect();
  const particles = [];
  
  for (let i = 0; i < 6; i++) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    particle.style.left = `${rect.left + rect.width / 2}px`;
    particle.style.top = `${rect.top + rect.height / 2}px`;
    
    document.body.appendChild(particle);
    particles.push(particle);
    
    // Animate particle
    const angle = (i / 6) * Math.PI * 2;
    const distance = 50 + Math.random() * 30;
    const x = Math.cos(angle) * distance;
    const y = Math.sin(angle) * distance;
    
    particle.animate([
      { transform: 'translate(0, 0) scale(1)', opacity: 1 },
      { transform: `translate(${x}px, ${y}px) scale(0)`, opacity: 0 }
    ], {
      duration: 800,
      easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
    }).onfinish = () => {
      document.body.removeChild(particle);
    };
  }
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
  
  // Enhanced features
  addCardHoverEffects();
  initParallax();
  enhanceCategorySelection();
  
  // Add CSS for notifications and particles
  const style = document.createElement('style');
  style.textContent = `
    .notification {
      position: fixed;
      top: 20px;
      right: 20px;
      background: var(--glass-bg);
      backdrop-filter: blur(20px);
      border: 1px solid var(--glass-border);
      border-radius: 16px;
      padding: 16px 20px;
      box-shadow: var(--glass-shadow);
      transform: translateX(100%);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      z-index: 1000;
      max-width: 300px;
    }
    
    .notification.show {
      transform: translateX(0);
    }
    
    .notification-content {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    
    .notification-text {
      color: var(--text-white);
      font-size: 14px;
      font-weight: 500;
    }
    
    .notification.success {
      border-color: var(--success);
    }
    
    .notification.warning {
      border-color: var(--warning);
    }
    
    .notification.error {
      border-color: var(--error);
    }
    
    .particle {
      position: fixed;
      width: 6px;
      height: 6px;
      background: linear-gradient(135deg, var(--coral), var(--purple));
      border-radius: 50%;
      pointer-events: none;
      z-index: 999;
    }
  `;
  document.head.appendChild(style);
});