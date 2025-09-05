// LocalBriefing JavaScript

let currentStep = 1;

function nextStep() {
    document.getElementById(`step${currentStep}`).style.display = 'none';
    currentStep++;
    document.getElementById(`step${currentStep}`).style.display = 'block';
}

function selectAll() {
    const items = document.querySelectorAll('.category-item');
    items.forEach(item => {
        item.classList.add('selected');
    });
}

function toggleSwitch(element) {
    element.classList.toggle('active');
}

// 카테고리 선택 토글
document.addEventListener('DOMContentLoaded', function() {
    const categoryItems = document.querySelectorAll('.category-item');
    categoryItems.forEach(item => {
        item.addEventListener('click', function() {
            this.classList.toggle('selected');
        });
    });
    
    // 구/동 선택 연동
    const guSelect = document.getElementById('gu-select');
    const dongSelect = document.getElementById('dong-select');
    
    if (guSelect && dongSelect) {
        guSelect.addEventListener('change', function() {
            dongSelect.innerHTML = '<option value="">동 선택</option>';
            
            if (this.value === 'gangnam') {
                dongSelect.innerHTML += `
                    <option value="yeoksam">역삼동</option>
                    <option value="nonhyeon">논현동</option>
                    <option value="daechi">대치동</option>
                `;
            } else if (this.value === 'seocho') {
                dongSelect.innerHTML += `
                    <option value="seocho">서초동</option>
                    <option value="banpo">반포동</option>
                    <option value="jamwon">잠원동</option>
                `;
            }
        });
    }
});