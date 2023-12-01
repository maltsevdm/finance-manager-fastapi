import React from "react";
import './SummaryBlock.css';

const SummaryBlock = ({sumData}) => {
    
    
    return (
        <div className="sum-block">
            <span>Баланс: {sumData.balance} рублей</span>
            <span>Доходы: {sumData.inc} рублей</span>
            <span>Расходы: {sumData.exp} рублей</span>
        </div>
    )
};

export default SummaryBlock;