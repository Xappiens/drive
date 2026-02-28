/**
 * Drive Attachments Integration
 * 
 * This bundle injects a Drive widget into Frappe form sidebars
 * when the integration is enabled. It replaces the default Frappe
 * attachments section with a Drive-powered file management.
 */

class DriveAttachmentsWidget {
    constructor(frm) {
        this.frm = frm;
        this.container = null;
        this.modal = null;
        this.escHandler = null;
        this.modalMessageHandler = null;
        this.render();
    }

    render() {
        const attachmentsSection = this.frm.attachments?.parent;
        if (!attachmentsSection) return;

        // Hide the original Frappe attachments section
        this.originalAttachments = $(attachmentsSection);
        this.originalAttachments.hide();

        // Create simple widget similar to other sidebar sections
        this.container = $(`
            <div class="drive-attachments-widget sidebar-menu">
                <a class="sidebar-label drive-manage-link">
                    <svg class="icon icon-sm" style="margin-right: 6px;">
                        <use href="#icon-folder-open"></use>
                    </svg>
                    <span>${__('Drive Attachments')}</span>
                    <span class="drive-open-external" title="${__('Open in new tab')}">
                        <svg class="icon icon-xs">
                            <use href="#icon-external-link"></use>
                        </svg>
                    </span>
                </a>
            </div>
        `);

        this.originalAttachments.after(this.container);

        this.container.find('.drive-manage-link').on('click', (e) => {
            if ($(e.target).closest('.drive-open-external').length) {
                e.preventDefault();
                e.stopPropagation();
                this.openInDrive();
            } else {
                this.openModal();
            }
        });
    }

    openModal() {
        if (this.modal) return;

        const doctype = encodeURIComponent(this.frm.doctype);
        const docname = encodeURIComponent(this.frm.docname);
        const embedUrl = `/drive/embed/${doctype}/${docname}?modal=1`;

        this.modal = $(`
            <div class="drive-modal-overlay">
                <div class="drive-modal">
                    <div class="drive-modal-header">
                        <span class="drive-modal-title">
                            <svg class="icon icon-md" style="margin-right: 8px;">
                                <use href="#icon-folder-open"></use>
                            </svg>
                            ${__('Attachments')}: ${this.frm.docname}
                        </span>
                        <div class="drive-modal-actions">
                            <button type="button" class="btn btn-sm btn-default drive-modal-external">
                                <svg class="icon icon-sm">
                                    <use href="#icon-external-link"></use>
                                </svg>
                                ${__('Open in Drive')}
                            </button>
                            <button type="button" class="btn btn-sm btn-default drive-modal-close">
                                <svg class="icon icon-sm">
                                    <use href="#icon-close"></use>
                                </svg>
                            </button>
                        </div>
                    </div>
                    <div class="drive-modal-body">
                        <div class="drive-modal-loading text-center text-muted">
                            ${__('Loading...')}
                        </div>
                        <iframe src="${embedUrl}" class="drive-modal-iframe"></iframe>
                    </div>
                </div>
            </div>
        `);

        $('body').append(this.modal);
        $('body').addClass('drive-modal-open');

        this.modal.find('.drive-modal-close').on('click', () => this.closeModal());
        this.modal.find('.drive-modal-external').on('click', () => this.openInDrive());
        this.modal.find('.drive-modal-overlay').on('click', (e) => {
            if ($(e.target).hasClass('drive-modal-overlay')) {
                this.closeModal();
            }
        });

        const iframe = this.modal.find('.drive-modal-iframe');
        iframe.on('load', () => {
            this.modal.find('.drive-modal-loading').hide();
            iframe.addClass('loaded');
        });

        this.escHandler = (e) => {
            if (e.key === 'Escape') this.closeModal();
        };
        $(document).on('keydown', this.escHandler);

        this.modalMessageHandler = (e) => this.handleModalMessage(e);
        window.addEventListener('message', this.modalMessageHandler);
    }

    handleModalMessage(event) {
        if (event.origin !== window.location.origin) return;
        if (!event.data || typeof event.data !== 'object') return;

        if (event.data.type === 'drive-file-uploaded' || event.data.type === 'drive-file-deleted') {
            this.frm.reload_doc();
        }
    }

    closeModal() {
        if (this.modal) {
            this.modal.remove();
            this.modal = null;
        }
        $('body').removeClass('drive-modal-open');
        if (this.escHandler) {
            $(document).off('keydown', this.escHandler);
            this.escHandler = null;
        }
        if (this.modalMessageHandler) {
            window.removeEventListener('message', this.modalMessageHandler);
            this.modalMessageHandler = null;
        }
    }

    openInDrive() {
        const doctype = encodeURIComponent(this.frm.doctype);
        const docname = encodeURIComponent(this.frm.docname);
        window.open(`/drive/attachments/${doctype}/${docname}`, '_blank');
    }

    destroy() {
        this.closeModal();
        if (this.container) {
            this.container.remove();
            this.container = null;
        }
        if (this.originalAttachments) {
            this.originalAttachments.show();
            this.originalAttachments = null;
        }
    }
}

function shouldShowWidget(frm) {
    const settings = frappe.boot.drive_integration;
    if (!settings?.enabled) return false;
    if (!settings?.embed_in_sidebar) return false;
    if (frm.doc.__islocal) return false;
    if (settings.excluded_doctypes?.includes(frm.doctype)) return false;
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
    if (!frappe.boot.drive_integration?.enabled) return;

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

    if (frappe.realtime) {
        frappe.realtime.on('drive_integration_settings_updated', (data) => {
            frappe.boot.drive_integration = {
                enabled: data.enabled,
                embed_in_sidebar: data.embed_in_sidebar,
                show_attachments_in_drive: data.show_attachments_in_drive,
                excluded_doctypes: data.excluded_doctypes || []
            };
            
            if (!data.enabled || !data.embed_in_sidebar) {
                $('.drive-attachments-widget').remove();
                $('.form-attachments').show();
                if (cur_frm?._drive_widget) {
                    cur_frm._drive_widget.destroy();
                    cur_frm._drive_widget = null;
                }
            } else if (cur_frm) {
                initDriveWidget(cur_frm);
            }
        });
    }
});
