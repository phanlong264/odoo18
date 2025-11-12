/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ShopManagementDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            platforms: [],
            selectedPlatform: null,
            shops: [],
        });

        onWillStart(async () => {
            await this.loadPlatforms();
        });
    }

    async loadPlatforms() {
        this.state.platforms = await this.orm.searchRead(
            "ecommerce.platform",
            [],
            ["id", "name", "code", "color", "shop_count"],
            { order: "sequence" }
        );
        if (this.state.platforms.length > 0) {
            await this.selectPlatform(this.state.platforms[0]);
        }
    }

    async selectPlatform(platform) {
        this.state.selectedPlatform = platform;
        this.state.shops = await this.orm.searchRead(
            "ecommerce.shop",
            [["platform_id", "=", platform.id]],
            ["id", "name", "shop_id", "status", "last_sync_date", "owner_name"]
        );
    }

    async openConnectWizard() {
        if (!this.state.selectedPlatform) return;
        
        this.action.doAction({
            type: "ir.actions.act_window",
            name: `Kết nối với ${this.state.selectedPlatform.name}`,
            res_model: "ecommerce.shop.connect.wizard",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            context: {
                default_platform_id: this.state.selectedPlatform.id,
            },
        });
    }

    async openShopForm(shopId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Chi tiết gian hàng",
            res_model: "ecommerce.shop",
            res_id: shopId,
            view_mode: "form",
            views: [[false, "form"]],
            target: "current",
        });
    }

    getStatusBadgeClass(status) {
        const statusMap = {
            'active': 'badge-success',
            'expired': 'badge-danger',
            'pending': 'badge-warning',
        };
        return statusMap[status] || 'badge-secondary';
    }

    getStatusLabel(status) {
        const labels = {
            'active': 'Kích hoạt',
            'expired': 'Hết hạn',
            'pending': 'Chờ kết nối',
        };
        return labels[status] || status;
    }

    formatDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleString('vi-VN');
    }
}

ShopManagementDashboard.template = "ecommerce_integration.ShopManagementDashboard";

registry.category("actions").add("shop_management_dashboard", ShopManagementDashboard);
