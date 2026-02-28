/**
 * Drive Attachments Integration
 * 
 * This bundle injects a Drive widget into Frappe form sidebars
 * when the integration is enabled.
 */

class DriveAttachmentsWidget {
    constructor(frm) {
        this.frm = frm;
        this.container = null;
        this.iframe = null;
        this.isCollapsed = false;
        this.render();
    }

    render() {
        const attachmentsSection = this.frm.attachments?.parent;
        if (!attachmentsSection) return;

        this.container = $(`
            <div class="drive-attachments-widget">
                <div class="drive-widget-header">
                    <span class="drive-widget-title">
                        ${frappe.utils.icon('folder-open', 'sm')}
                        <span>${__('Drive')}</span>
                    </span>
                    <div class="drive-widget-actions">
                        <button class="btn btn-xs btn-default drive-open-btn" title="${__('Open in Drive')}">
                            ${frappe.utils.icon('external-link', 'xs')}
                        </button>
                        <button class="btn btn-xs btn-default drive-toggle-btn" title="${__('Toggle')}">
                            ${frappe.utils.icon('down', 'xs')}
                        </button>
                    </div>
                </div>
                <div class="drive-widget-body">
                    <div class="drive-widget-loading">
                        <span class="text-muted">${__('Loading Drive...')}</span>
                    </div>
                </div>
            </div>
        `);

        $(attachmentsSection).after(this.container);

        this.container.find('.drive-toggle-btn').on('click', () => this.toggle());
        this.container.find('.drive-open-btn').on('click', () => this.openInDrive());

        this.loadIframe();
    }

    loadIframe() {
        const doctype = encodeURIComponent(this.frm.doctype);
        const docname = encodeURIComponent(this.frm.docname);
        const embedUrl = `/drive/embed/${doctype}/${docname}`;

        this.iframe = $(`
            <iframe 
                src="${embedUrl}"
                class="drive-embed-iframe"
                frameborder="0"
                loading="lazy"
            ></iframe>
        `);

        this.iframe.on('load', () => {
            this.container.find('.drive-widget-loading').hide();
            this.iframe.show();
        });

        this.iframe.on('error', () => {
            this.container.find('.drive-widget-loading').html(`
                <span class="text-muted">${__('Could not load Drive')}</span>
            `);
        });

        this.container.find('.drive-widget-body').append(this.iframe);

        window.addEventListener('message', (e) => this.handleMessage(e));
    }

    handleMessage(event) {
        if (!event.data || typeof event.data !== 'object') return;

        switch (event.data.type) {
            case 'drive-file-uploaded':
            case 'drive-file-deleted':
                this.frm.sidebar?.reload_docinfo();
                break;
            case 'drive-resize':
                if (event.data.height && this.iframe) {
                    this.iframe.css('height', Math.min(event.data.height, 400) + 'px');
                }
                break;
        }
    }

    toggle() {
        this.isCollapsed = !this.isCollapsed;
        this.container.find('.drive-widget-body').slideToggle(200);
        this.container.find('.drive-toggle-btn').html(
            frappe.utils.icon(this.isCollapsed ? 'right' : 'down', 'xs')
        );
    }

    openInDrive() {
        const doctype = encodeURIComponent(this.frm.doctype);
        const docname = encodeURIComponent(this.frm.docname);
        window.open(`/drive/attachments/${doctype}/${docname}`, '_blank');
    }

    destroy() {
        if (this.container) {
            this.container.remove();
        }
    }
}

function shouldShowWidget(frm) {
    const settings = frappe.boot.drive_integration;
    
    if (!settings?.enabled) return false;
    if (!settings?.embed_in_sidebar) return false;
    if (frm.doc.__islocal) return false;
    
    if (settings.excluded_doctypes?.includes(frm.doctype)) {
        return false;
    }
    
    return true;
}

function initDriveWidget(frm) {
    if (frm._drive_widget) {
        frm._drive_widget.destroy();
        frm._drive_widget = null;
    }

    if (shouldShowWidget(frm)) {
        frm._drive_widget = new DriveAttachmentsWidget(frm);
    }
}

$(document).ready(() => {
    if (!frappe.boot.drive_integration?.enabled) {
        return;
    }

    $(document).on('form-refresh', (event, frm) => {
        if (frm && frm.doctype && frm.docname) {
            setTimeout(() => initDriveWidget(frm), 100);
        }
    });

    if (typeof frappe.ui?.form?.on === 'function') {
        const originalRefresh = frappe.ui.form.Form.prototype.refresh;
        frappe.ui.form.Form.prototype.refresh = function(...args) {
            const result = originalRefresh.apply(this, args);
            if (this.frm) {
                setTimeout(() => initDriveWidget(this.frm), 100);
            }
            return result;
        };
    }
});
