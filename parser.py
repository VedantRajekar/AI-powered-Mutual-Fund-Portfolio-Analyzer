import pandas as pd

def parse_cas_pdf(file_path: str, password: str = "") -> dict:
    """
    Parse real CAMS/Kfintech CAS PDF.
    Raises error if file is invalid — does NOT fall back to demo data.
    """
    try:
        import casparser
        data = casparser.read_cas_pdf(file_path, password)

        if data.investor_info is None:
            raise ValueError(
                "Could not read this PDF.\n\n"
                "Please make sure:\n"
                "1. This is an official CAS PDF from CAMS or Kfintech\n"
                "2. The password is your registered email address\n"
                "3. The PDF is not corrupted or password protected incorrectly"
            )

        return extract_portfolio(data)

    except casparser.exceptions.CASParseError as e:
        raise ValueError(f"Invalid CAS format: {e}")
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse CAS PDF: {e}")


def extract_portfolio(cas_data) -> dict:
    """Extract real holdings from parsed CAS data."""
    holdings    = []
    total_value = 0

    for folio in cas_data.folios:
        for scheme in folio.schemes:
            if scheme.valuation and scheme.valuation.value:
                value = float(scheme.valuation.value)
                total_value += value

                # Try to get invested value from transactions
                invested = calculate_invested(scheme)

                holdings.append({
                    "fund_name":     scheme.scheme,
                    "folio":         folio.folio,
                    "amc":           folio.amc,
                    "units":         float(scheme.close or 0),
                    "nav":           float(scheme.valuation.nav or 0),
                    "current_value": value,
                    "invested":      invested,
                    "isin":          scheme.isin or "",
                    "amfi_code":     scheme.amfi or ""
                })

    if not holdings:
        raise ValueError(
            "No fund holdings found in this CAS PDF.\n"
            "The statement may be empty or for a period with no transactions."
        )

    df = pd.DataFrame(holdings)
    df["allocation_pct"] = (
        df["current_value"] / total_value * 100
    ).round(2)

    total_invested = df["invested"].sum()

    return {
        "holdings":         df,
        "total_value":      round(total_value, 2),
        "total_invested":   round(total_invested, 2),
        "investor_name":    cas_data.investor_info.name
                            if cas_data.investor_info else "Investor",
        "statement_period": str(getattr(cas_data, "statement_period", ""))
    }


def calculate_invested(scheme) -> float:
    """
    Calculate total amount invested in a scheme
    by summing all purchase transactions.
    Returns estimated value if transactions not available.
    """
    try:
        invested = 0.0
        if hasattr(scheme, "transactions") and scheme.transactions:
            for txn in scheme.transactions:
                # Count purchases, SIPs, switches-in as invested amount
                if hasattr(txn, "amount") and txn.amount:
                    amount = float(txn.amount)
                    txn_type = str(getattr(txn, "type", "")).upper()

                    # Add inflow transactions
                    if any(keyword in txn_type for keyword in [
                        "PURCHASE", "SIP", "SWITCH IN",
                        "SYSTEMATIC", "NFO", "REINVEST"
                    ]):
                        if amount > 0:
                            invested += amount

        # If no transaction data, estimate from NAV history
        if invested == 0 and hasattr(scheme, "valuation"):
            current_value = float(scheme.valuation.value or 0)
            # Conservative estimate — assume 85% of current value invested
            invested = current_value * 0.85

        return round(invested, 2)

    except Exception:
        # Last resort estimate
        current_value = float(
            scheme.valuation.value
        ) if scheme.valuation else 0
        return round(current_value * 0.85, 2)