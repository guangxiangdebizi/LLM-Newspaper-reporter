/**
 * 主JavaScript文件
 * 包含通用功能函数
 */

// 日期时间格式化函数
function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return '-';
    const date = new Date(dateTimeStr);
    return date.toLocaleString('zh-CN');
}

// 文件大小格式化函数
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 显示通知消息
function showToast(message, type = 'success') {
    // Bootstrap 5 Toast 组件的简单实现
    const toastContainer = document.getElementById('toast-container');
    
    // 如果容器不存在，创建一个
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    // 创建 Toast 元素
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    // Toast 内容
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // 添加到容器中
    document.getElementById('toast-container').appendChild(toastEl);
    
    // 创建 Bootstrap Toast 实例并显示
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 3000
    });
    toast.show();
    
    // 自动移除元素
    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}

// 处理API错误
function handleApiError(error) {
    console.error('API错误:', error);
    
    let errorMessage = '操作失败';
    
    if (error.response) {
        // 服务器响应了错误信息
        errorMessage = error.response.data.message || `服务器错误: ${error.response.status}`;
    } else if (error.request) {
        // 请求已发送但未收到响应
        errorMessage = '无法连接到服务器，请检查网络连接';
    } else {
        // 请求设置时出错
        errorMessage = error.message || '发送请求时出错';
    }
    
    showToast(errorMessage, 'danger');
} 