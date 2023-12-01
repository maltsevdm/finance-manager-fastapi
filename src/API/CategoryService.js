import axios from "axios";
import {url_categories, url_icons, url_icon} from "../config.js";

export default class CategoryService {
    static async getExpense () {
        const response = await axios.get(url_categories + 'expense')
        return response.data
    }

    static async getIncome () {
        const response = await axios.get(url_categories + 'income')
        return response.data
    }
}